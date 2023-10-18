import argparse
import logging
from typing import List
import json
from pathlib import Path
import yaml
from utilities.assets.Alias import Alias
from utilities.assets.MultistageAlias import MultistageAlias
from utilities.connection.ApigwUtil import ApigwUtil
from utilities.assets.Api import Api
from utilities.assets.Application import Application
from utilities.assets.AliasFactory import AliasFactory
from utilities.assets.Policy import Policy

my_logger = logging.getLogger("agw-staging")

def check_applications(apigw_connect: ApigwUtil) -> bool:
    found_applications: list[Application] | None = apigw_connect.get_assets("applications")
    if found_applications is None:
        my_logger.warning("no applications found!")
        return True

    for my_app in found_applications:
        #logger.debug(app)
        if not (my_app.name.lower().endswith(("_dev", "_test", "_qs", "_prod")) or my_app.name.lower().__eq__("ESB-TestClient_oAuth2")):
            my_logger.error(f"Application name {my_app.name} doesnt end with \"_environment-name\" (DEV, TEST, QS, PROD)")
            return False

    my_logger.info("checking applications was succesful!")    
    return True
    

def delete_unused_applications(apigw_connect: ApigwUtil, stage) -> bool:
    found_applications: list[Application] | None = apigw_connect.get_assets("applications")
    if found_applications is None:
        my_logger.warning("no applications found!")
        return True

    for my_app in found_applications:
        
        if not my_app.name.lower().endswith(f"_{stage}"):
            my_logger.debug(f"deleting application {my_app.name} with ID: {my_app.id}")
            status_code = apigw_connect.delete_asset(my_app)
            if status_code != 204:
                my_logger.error(f"deletion of application {my_app.name} FAILED! Aborting")
                return False
            my_logger.info(f"deleted application {my_app.name}")
            continue
        
        if my_app.is_suspended:
            my_logger.debug(f"activating application {my_app.name} with ID: {my_app.id}")
            status_code = apigw_connect.activate_application(my_app)
            if status_code > 200:
                my_logger.error(f"activation of application {my_app.name} FAILED! Aborting")
                return False
            my_logger.info(f"activated application {my_app.name}")

    my_logger.info("deleting unused applications was succesful!")          
    return True


def update_alias_from_multistage(apigw_connect: ApigwUtil, aliases_path: Path, stage: str) -> bool:
    """Updates build gateway aliases with the values from aliases.json.
    
    This function assumes that aliases are maintained in the repository.
    The MultistageAlias classes are a composition and store the original alias and the stage-specific values.
    """
    # update aliases for target stage value
    with aliases_path.open() as json_file:
        multistage_payload_list = json.loads(json_file.read())
    
    # get aliases from build gateway
    found_aliases: List[Alias] | None = apigw_connect.get_assets("alias") 
    if found_aliases is None:
        my_logger.warning("no aliases found!")
        return True
    
    for multistage_payload in multistage_payload_list:
        my_multistage_alias = MultistageAlias(multistage_payload)
        my_logger.debug(my_multistage_alias)

        for my_alias in found_aliases:
            if my_multistage_alias.name != my_alias.name:
                continue
            
            my_logger.debug(f"updating alias {my_alias}")
            my_alias.update_alias(my_multistage_alias.get_connection_details_by_stage(stage))
            status_code = apigw_connect.update_asset(my_alias)
            if status_code > 200:
                my_logger.error(f"updating alias {my_alias.name} FAILED! Aborting")
                return False
            my_logger.info(f"updated alias {my_alias}")
           
    return True


def update_aliases(apigw_connect: ApigwUtil, workspace: str, stage: str) -> bool:
    """updates build gateway aliases with the values from target-stage config.
    
    This function assumes that aliases are maintained in the Api Gateways.
    """
    
    global_aliases = []
    target_stage_aliases: List[dict] = load_alias_config(workspace, stage)
    if target_stage_aliases == [] or target_stage_aliases is None:
        my_logger.error(f"Couldn't find any aliases in configuration folder! Please export AGW config from target-stage using the pipeline!")
        return False
    
    # get aliases after API import
    found_aliases: list[Alias] | None = apigw_connect.get_assets("alias")     
    if found_aliases is None:
        my_logger.warning("no aliases found!")
        return True

    for my_alias in found_aliases:          
        my_logger.debug(f"updating alias {my_alias.name}")
        # update aliases for target stage    
        for alias in target_stage_aliases:
            alias_name: str = alias.get("name", "not set")
            # if alias w/ name is present and target_stage --> update
            if alias_name == my_alias.name: 
                my_alias.update_alias(alias)              
                status_code = apigw_connect.update_asset(my_alias)
                if status_code > 200:
                    my_logger.error(f"updating alias {alias_name} FAILED! Aborting")
                    return False
                my_logger.info(f"updated alias {alias_name}")

    # TODO X: import global aliases
    for alias_payload in global_aliases:
        my_alias = AliasFactory.create_alias(alias_payload)
        if my_alias is None:
            my_logger.warning(f"Alias could not be created, skipping alias!")
            continue
            
        my_logger.debug(f"updating alias {my_alias.name}")
        status_code = apigw_connect.create_asset(my_alias)
        if status_code > 200:
            my_logger.error(f"creating alias {my_alias.name} FAILED! Aborting")
            return False
        my_logger.info(f"created alias {my_alias.name}")
    
    my_logger.info("checking aliases was succesful!")  
    return True


def load_alias_config(workspace: str, stage: str) -> list:
    target_stage_aliases: List[dict] = []
    # globb all files, iterate and move into json as list
    alias_path = Path(f"{workspace}/environments/{stage.upper()}/assets/Alias")
    alias_files_list =  list(alias_path.glob('*'))
    my_logger.debug(f"Number of aliases in {alias_path}: {len(alias_files_list)}")
    for alias_file in alias_files_list:
        with open(str(alias_file)) as file:
            alias = json.load(file)
            target_stage_aliases.append(alias)
            
    return target_stage_aliases
    

def add_tags_to_apis(apigw_connect: ApigwUtil, tag_list: List[str]) -> bool:
    found_apis: List[Api] | None = apigw_connect.get_assets("apis")    
    
    if found_apis is None:
        my_logger.warning("no aliases found!")
        return True

    for my_api in found_apis:
        # TODO X: validate api naming conventions
        # Add Tags to API
        my_api.add_tags(tag_list)
        status_code = apigw_connect.update_asset(my_api)
        if status_code > 200:
            my_logger.error(f"updating API {my_api.name} FAILED! Aborting")
            return False
        my_logger.debug(f"updated API {my_api.name} with tags {tag_list} - status code {status_code}")

    my_logger.info("checking API was succesful!")          
    return True


def check_policies(apigw_connect: ApigwUtil, policy_blacklist_list: List[str]) -> bool:
    found_policies: List[Policy] | None = apigw_connect.get_assets("policyActions")  
    if found_policies is None:
        my_logger.warning("no policies found!")
        return True
    
    my_logger.debug(f"current blacklist: {policy_blacklist_list}")
    for my_policy in found_policies:
        if (my_policy.kind in policy_blacklist_list) and (my_policy.id != "GlobalLogInvocationPolicyAction"):
            my_logger.error(f"{my_policy.kind} policy not allowed on API level. Blacklist: {policy_blacklist_list}")
            return False
    
    my_logger.info("checking logging policies was succesful!")  
    return True


def prepare_stage(apigw_connect: ApigwUtil, workspace: str, stage: str, api_project: str, build_id: str, settings_dict: dict) -> None:
    if settings_dict["check_policies"]:
        if not check_policies(apigw_connect, settings_dict["policy_blacklist"]):
            my_logger.error(f"check_policies() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
    
    if not check_applications(apigw_connect):
        my_logger.error(f"check_applications() failed. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return

    if not delete_unused_applications(apigw_connect, stage):
        my_logger.error(f"delete_unused_applications() failed. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return
        
    aliases_path = Path(f"{workspace}/apis/{api_project}/aliases.json")
    if aliases_path.is_file():
        if not update_alias_from_multistage(apigw_connect, aliases_path, stage):
            my_logger.error(f"update_alias_from_multistage() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
    else:
        if not update_aliases(apigw_connect, workspace, stage):
            my_logger.error(f"update_aliases() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
    
    if settings_dict["api_add_tags"]:
        if settings_dict["add_buildId_tag"]:
            new_set = set(settings_dict["tag_list"] + [f"BuildId: {build_id}"])
            settings_dict["tag_list"] = list(new_set)
        if not add_tags_to_apis(apigw_connect, settings_dict["tag_list"]):
            my_logger.error(f"check_api() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return

    my_logger.info(f"Preparing build environment was successful!")
    return


def main(workspace: str, target_environment_config: str, agw_user: str, agw_password: str, stage: str, hostname: str, port: int, use_ssl: bool, api_project: str, build_id: str):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
        
    settings_file = Path(f"{workspace}/configuration/{target_environment_config}")
    settings_dict = {"test_condition": True, "api_add_tags": True, "tag_list": [f"BuildId: {build_id}"], "check_policies": True, "policy_blacklist": []}
    if settings_file.exists():
        with settings_file.open() as file:
            settings = yaml.safe_load(file)
        try:    
            settings_dict.update(settings["build"])
        except KeyError:
            my_logger.info(f"'build' not set in {settings_file}. Using default values.")
    
    prepare_stage(agw_connection, workspace, stage, api_project, build_id, settings_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('workspace', type=str, help='path of the workspace')
    parser.add_argument('target-env', type=str, help='target AGW env')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('stage', type=str, help='stage to prepare')
    parser.add_argument('hostname', type=str, help='buildserver hostname')
    parser.add_argument('port', type=int, help='buildserver port')
    parser.add_argument('api-project', type=str, help='name of the api project')
    parser.add_argument('build-id', type=str, help='commit id of the current build')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    workspace = args.get('workspace', "not declared")
    target_env_config = args.get('target-env', "not declared")
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    stage = args.get('stage', "not declared").lower()
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    api_project = args.get('api-project', "not declared")
    BUILDID = args.get('build-id', "dfhrt756zrt")
    USE_SSL: bool = not args.get('no_ssl', False)
    main(workspace, target_env_config, agw_user, agw_password, stage, hostname, port, USE_SSL, api_project, BUILDID)
    