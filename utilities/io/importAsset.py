import argparse
import logging
from typing import List
from utilities.connection.ApigwUtil import ApigwUtil

my_logger = logging.getLogger("agw-staging")


def import_asset(file_path: str, overwrite_params: List[str], agw_connection: ApigwUtil) -> bool:
    status_code = agw_connection.import_asset(file_path, overwrite_params)
    if status_code > 201:
        my_logger.error(f"Importing {file_path} failed. Aborting!")
        return False

    return True


def main(file_path: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool, overwrite_aliases: bool):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
        
    my_logger.debug(f"overwrite: {overwrite_aliases}")
    overwrite_params = ["apis", "policies", "policyactions", "applications", "gatewayScopes"]
    if overwrite_aliases:
        overwrite_params.append("aliases")
        
    if not import_asset(file_path, overwrite_params, agw_connection):
        my_logger.error(f"import_asset() failed. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return
    
    my_logger.info(f"Importing file {file_path} was successful!")
    return
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('hostname', type=str, help='buildserver hostname')
    parser.add_argument('port', type=int, help='buildserver port')
    parser.add_argument('archive-path', type=str, help='path to the zip archive')
    parser.add_argument('overwrite-aliases', type=str, nargs='?', default="false", help='bool for overwriting aliases in API GW')
    parser.add_argument('--testing', action='store_true', help='bool for testing')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    file_path = args.get('archive-path', "not declared")
    OVERWRITE_ALIASES: bool = args.get('overwrite-aliases', "False").lower() == "true"
    TESTING: bool = args.get('testing', False)
    USE_SSL: bool = not args.get('no_ssl', False)
    main(file_path, agw_user, agw_password, hostname, port, USE_SSL, OVERWRITE_ALIASES)
