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


def prepare_stage(apigw_connect: ApigwUtil) -> None:
    if not delete_unused_applications(apigw_connect, stage):
        my_logger.error(f"delete_unused_applications() failed. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return

    my_logger.info(f"Post-test preparing build environment was successful!")
    return


def main(workspace: str, target_environment_config: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool, build_id: str):
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
    
    prepare_stage(agw_connection)

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
    parser.add_argument('--testing', action='store_true', help='bool for testing')
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
    main(workspace, target_env_config, agw_user, agw_password, hostname, port, USE_SSL, BUILDID)
    