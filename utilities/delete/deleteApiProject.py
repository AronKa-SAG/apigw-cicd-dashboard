import argparse
import json
import logging
from pathlib import Path
from typing import Tuple, Type
from utilities.assets.Api import Api
from utilities.assets.Asset import Asset
from utilities.assets.AssetFactory import AssetFactory
from utilities.connection.ApigwUtil import ApigwUtil

my_logger = logging.getLogger("agw-staging")


def get_asset_types_in_export_payload(workspace: str, api_project_name: str) -> list[str] | None:
    list_of_asset_types = ["Alias", "API"]
    
    export_payload_path = Path(f"{workspace}/apis/{api_project_name}/export_payload.json")
    if not export_payload_path.is_file:
        my_logger.error(f"Path {export_payload_path} doesn't exist! Probably wrong API project name.")
        return None
    
    with export_payload_path.open() as file:
        export_payload = json.load(file)
    
    if export_payload["includeOptions"]["includeApplications"]:
        list_of_asset_types.insert(0, "Application")
        
    if "gateway_scope" in export_payload["types"]:
        list_of_asset_types.append("GatewayScope")
    
    my_logger.debug(f"found asset types: {list_of_asset_types}")       
    my_logger.info(f"Succesfully retrieved asset types from {api_project_name} folder.")
    return list_of_asset_types
        

def get_assets_in_project(workspace: str, agw_connection: ApigwUtil, api_project_name: str, list_of_asset_types: list) -> list[Asset] | None:
    export_asset_type_mapping = {
        "Alias": "alias", 
        "API": "apis",
        "Application": "applications",
        "GatewayScope": "scopes"
    }
    asset_list = []
    export_path = Path(f"{workspace}/apis/{api_project_name}/assets")
    if not export_path.exists:
        my_logger.error(f"Path {export_path} doesn't exist! Probably wrong API project name.")
        return None
    
    for asset_type in list_of_asset_types:
        asset_path: Path = export_path / asset_type
        asset_glob = list(asset_path.glob(f"*/{asset_type}*"))
        my_logger.debug(f"found {asset_type} files: {asset_glob}")
        for asset in asset_glob:
            asset_id = asset.suffix[1:]
            my_logger.debug(f"getting {asset_type} with id: {asset_id}")
            my_asset = agw_connection.get_asset_by_id(export_asset_type_mapping[asset_type], asset_id)
            if my_asset is None:
                my_logger.warning(f"failed to create {asset_type} with id: {asset_id}")
                continue
            my_logger.debug(f"created asset {my_asset}")
            asset_list.append(my_asset)
    
    my_logger.info(f"Succesfully created asset in {api_project_name} folder.")    
    return asset_list
            

def delete_assets(asset_list: list[Asset], agw_connection: ApigwUtil) -> Tuple[bool, str]:
    successful_deletions = []
    failed_deletions = []
    
    for asset in asset_list:
        if type(asset) is Api:
            if asset.is_active:
                my_logger.warning(f"Api {api_project_name} is active. Deactivating API.")
                if not api_set_state(agw_connection, asset, False):
                    my_logger.error(f"Deactivating API {asset.name} failed! Aborting deletion process.")
                    return (False, f"Could not update API {asset.name}!")
                my_logger.debug(f"Successfully deactivated API {asset.name}.")
            
        response_code = agw_connection.delete_asset(asset)
        if 199 < response_code < 300:
            successful_deletions.append(asset.name)
        else:
            failed_deletions.append(asset.name)
            
    my_logger.info(f"Finished deleting assets. Successful deletions: {len(successful_deletions)}. Failed deletions: {len(failed_deletions)}")
    my_logger.debug(f"Successful deletions: {successful_deletions}")
    my_logger.debug(f"Failed deletions: {failed_deletions}")

    if len(failed_deletions) == 0:
        return (True, "All deletions were successful.")
    else:
        return (False, f"Number of failed deletions: {len(failed_deletions)}")
    
       
def api_set_state(agw_connection: ApigwUtil, my_api: Api, state: bool) -> bool:
    status_code = agw_connection.api_set_active(my_api, state)
    
    if status_code > 200:
        my_logger.error(f"Activating API {my_api.name} FAILED! Aborting")
        return False
    
    state_string = "Activating" if state else "Deactivating"
    my_logger.info(f"{state_string} API {my_api.name} was succesful!")
    return True


def main(workspace: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool, api_project_name: str):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)

    asset_type_list = get_asset_types_in_export_payload(workspace, api_project_name)
    if asset_type_list is None:
        my_logger.error(f"Could not delete assets of {api_project_name}.")
        return
    
    asset_list = get_assets_in_project(workspace, agw_connection, api_project_name, asset_type_list)
    if asset_list is None:
        my_logger.error(f"Could not delete assets of {api_project_name}.")
        return
    
    success, responsetext = delete_assets(asset_list, agw_connection)
       
    if success:
        my_logger.info(responsetext)
    else:
        my_logger.error(responsetext)
        print(f"##vso[task.logissue type=error]Reason: {responsetext}")
        print("##vso[task.complete result=Failed;]")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('workspace', type=str, help='path of the workspace')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('hostname', type=str, help='agw server hostname')
    parser.add_argument('port', type=int, help='agw server port')
    parser.add_argument('api-project-name', type=str, help='name of the api to delete')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    workspace = args.get('workspace', "not declared")
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    api_project_name = args.get('api-project-name', "not declared")
    USE_SSL: bool = not args.get('no_ssl', False)
    main(workspace, agw_user, agw_password, hostname, port, USE_SSL, api_project_name)