import argparse
import logging
import json
import yaml
from utilities.connection.ApigwUtil import ApigwUtil
from utilities.assets.GatewayScope import GatewayScope
from pathlib import Path

my_logger = logging.getLogger("agw-staging")


def create_export_json(workdir: str, new_asset_types: list, keyword_ids: str, export_applications: bool) -> dict:
    with open(f"{workdir}/utilities/templates/export_payload_api.json", 'r') as f:
        export_payload_dict = json.load(f)
    
    asset_types: list = export_payload_dict["types"]    
    if new_asset_types:    
        asset_types += new_asset_types
        
    export_payload_dict["types"] = asset_types 
    export_payload_dict["scope"][0]["keyword"] = keyword_ids   
    my_logger.debug(f"updated ids with {keyword_ids} and types with {asset_types}")
    
    if not export_applications:
        export_payload_dict["includeOptions"]["includeApplications"] = False
        
    return export_payload_dict


def get_scopes(apigw_connect: ApigwUtil, exception_list: list, api_ids: str):
    scopes_to_add_in_json: list[dict] = []
    added_gateway_scope: bool = False
    ids_to_add_in_export_payload: str = api_ids.replace(',', '|')
    
    # get all gatewayScopes from export-stage
    gateway_scope_list: list[GatewayScope] | None = apigw_connect.get_assets("scopes")
    if gateway_scope_list is None or len(gateway_scope_list) < 1: 
        my_logger.warning(f"Didn't find any GatewayScopes in the API Gateway!")
        return [], ids_to_add_in_export_payload, added_gateway_scope
    
    # loop over gatewayScopes and find api dependet scopes
    for gateway_scope in gateway_scope_list:
        my_logger.debug(f"Processing {gateway_scope} with name {gateway_scope.name}")
        my_logger.debug(f"Check if name is included in exception_list: {exception_list}")
        if gateway_scope.name in exception_list:
            my_logger.debug(f"Skip {gateway_scope.name}")
            continue

        # api_id in scope: add scope_id, add requiredAuthScopes
        if gateway_scope.references_apis(api_ids):
            my_logger.debug(f"gw_scope {gateway_scope} includes APIs {api_ids}")
            ids_to_add_in_export_payload += f"|{gateway_scope.id}"
            added_gateway_scope = True
            for required_scope in gateway_scope.required_auth_scopes:
                scopes_to_add_in_json.append({
                    "name": required_scope["scopeName"],
                    "description": gateway_scope.description
                })
    my_logger.debug(f"returning new scopes: {scopes_to_add_in_json} and added_gw_scope: {added_gateway_scope}")
    return scopes_to_add_in_json, ids_to_add_in_export_payload, added_gateway_scope


def create_export_payload_file(apigw_connect: ApigwUtil, workdir: str, api_project: str, api_ids: str, exception_list: list, export_applications: bool) -> bool:
    additional_asset_types = []
    my_logger.debug(f"exception_list: {exception_list}")
    scopes_to_add_in_json, ids_to_add_in_export_payload, added_gateway_scope = get_scopes(apigw_connect, exception_list, api_ids)
    
    # create api-project folder
    path = Path(f"{workdir}/apis/{api_project}")
    path.mkdir(parents=True, exist_ok=True)    
          
    # create scopes.json file
    if len(scopes_to_add_in_json) > 0 :
        my_logger.debug(f"Scopes to add: {scopes_to_add_in_json}")
        scope_path = path / "scopes.json"
        with scope_path.open('w') as f:
            json.dump(scopes_to_add_in_json, f, ensure_ascii= False, indent=4)
    else:
        my_logger.warning(f"No Scopes to write into scopes.json for {api_project} API!")
    
    # create export_payload.json file
    if added_gateway_scope:
        additional_asset_types.append("gateway_scope")
    export_payload_dict = create_export_json(workdir, additional_asset_types, str(ids_to_add_in_export_payload), export_applications)
    my_logger.debug(f"new export_payload.json for {api_project}: {str(export_payload_dict)}")
    payload_path = path / "export_payload.json"
    with payload_path.open('w') as f:
        json.dump(export_payload_dict, f, ensure_ascii= False, indent=4)

    my_logger.info(f"successfully created /export_payload.json and /scopes.json for {api_project}!")
    return True


def main(workspace: str, source_environment_config: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool, api_project: str, api_ids: str):
    my_logger.debug("Read variables and prepare Scopes for export_payload for " + api_project + " API ID: " + api_ids)
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
    
    settings_file = Path(f"{workspace}/configuration/{source_environment_config}")
    gw_scope_exceptions = []
    export_applications = False
    my_logger.debug(f"Reading environment settings file: {settings_file}")
    if settings_file.exists():
        with settings_file.open() as file:
            settings = yaml.safe_load(file)
        try:    
            gw_scope_exceptions = settings["io"]["scope_exceptions"]
            export_applications = settings["io"]["export_apps"]
#            my_logger.debug(f"settings: {settings}")
            my_logger.debug(f"gw_scope_exceptions: {gw_scope_exceptions}")
            my_logger.debug(f"export_applications: {export_applications}")
        except KeyError:
            my_logger.info(f"scope_exceptions or export_apps not set in {settings_file}. Using default values.")
    
    
    if not create_export_payload_file(agw_connection, workspace, api_project, api_ids, exception_list=gw_scope_exceptions, export_applications=export_applications):
        my_logger.error(f"create_export_payload_file() failed. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return
    
    my_logger.info("Preparing export payload was successful!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('workspace', type=str, help='path of the workspace')
    parser.add_argument('source-env', type=str, help='source AGW env')
    parser.add_argument('agw-user', type=str, help='API Gateway export user')
    parser.add_argument('agw-password', type=str, help='API Gateway export user password')
    parser.add_argument('hostname', type=str, help='source AGW env hostname')
    parser.add_argument('port', type=int, help='source AGW env port')
    parser.add_argument('api-project', type=str, help='name of the api')
    parser.add_argument('api-id', type=str, help='api ids, comma separated if multiple')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    workspace = args.get('workspace', "not declared")
    source_env_config = args.get('source-env', "not declared")
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    api_project = args.get('api-project', "not declared")
    api_ids = args.get('api-id', "not declared")
    USE_SSL: bool = not args.get('no_ssl', False)
    main(workspace=workspace, source_environment_config=source_env_config ,agw_user=agw_user, agw_password=agw_password, hostname=hostname, port=port, use_ssl=USE_SSL, api_project=api_project, api_ids=api_ids)
