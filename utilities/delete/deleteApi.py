import argparse
import logging
from typing import Tuple
from utilities.assets.Api import Api
from utilities.connection.ApigwUtil import ApigwUtil

my_logger = logging.getLogger("agw-staging")


def get_api_based_on_apiName(api_name, agw_connection: ApigwUtil):
    response_json = agw_connection.get_asset_by_name("api", api_name)["api"]
    
    if len(response_json) == 0:
        print(f"##vso[task.logissue type=error]Api {api_name} does not exist on the target environment!")
        print("##vso[task.complete result=Failed;]")
        return None
    
    if len(response_json) > 1:
        print(f"##vso[task.logissue type=error]More then 1 ApiID found based on {api_name} Please contact Operations Team.")
        print("##vso[task.complete result=Failed;]")
        return None
    
    found_api: Api | None = agw_connection.get_asset_by_id("apis", response_json[0]["id"])    
    if found_api is None:
        print("##vso[task.logissue type=warning]The API could not be loaded.")
        return None
        
    my_logger.info(f"Succesfully retrieved API {api_name}.")
    return found_api
        

def delete_api(api: Api, agw_connection: ApigwUtil) -> Tuple[bool, str]:
    response_code = agw_connection.delete_asset(api)
    if 199 < response_code < 300:
        return True, f"Successfully deleted API {api.name}."
    elif response_code == 404:
        return False, f"Couldn't delete API {api.name}."
    else:
        return False, "Something went wrong. Please contact Operations team."


def api_set_state(agw_connection: ApigwUtil, my_api: Api, state: bool) -> bool:
    status_code = agw_connection.api_set_active(my_api, state)
    
    if status_code > 200:
        my_logger.error(f"Activating API {my_api.name} FAILED! Aborting")
        return False
    
    state_string = "Activating" if state else "Deactivating"
    my_logger.info(f"{state_string} API {my_api.name} was succesful!")
    return True



def main(agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool, api_name: str):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
    
    api = get_api_based_on_apiName(api_name.replace(" ", ""), agw_connection)
    
    if api is None:
        my_logger.error(f"Could not delete API {api_name}.")
        return
    
    if api.is_active:
        my_logger.warning(f"Api {api_name} is active. Deactivating API.")
        if not api_set_state(agw_connection, api, False):
            my_logger.error(f"Deactivating API {api_name} failed! Aborting deletion process.")
            return None
        my_logger.debug(f"Successfully deactivated API {api_name}.")
    
    my_logger.debug(f"Found Api with ID {api.id} based on ApiName {api_name}")
    success, responsetext = delete_api(api, agw_connection)
    if success:
        my_logger.info(responsetext)
    else:
        my_logger.error(responsetext)
        print(f"##vso[task.logissue type=error]Reason: {responsetext}")
        print("##vso[task.complete result=Failed;]")
          
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('hostname', type=str, help='agw server hostname')
    parser.add_argument('port', type=int, help='agw server port')
    parser.add_argument('api-name', type=str, help='name of the api to delete')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    api_name = args.get('api-name', "not declared")
    USE_SSL: bool = not args.get('no_ssl', False)
    main(agw_user, agw_password, hostname, port, USE_SSL, api_name)