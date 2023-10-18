import argparse
import logging
from utilities.connection.ApigwUtil import ApigwUtil

my_logger = logging.getLogger("agw-staging")


def export_asset(file_path: str, payload_path: str, agw_connection: ApigwUtil) -> bool:
    status_code = agw_connection.export_asset(file_path, payload_path) 
    if status_code > 201:
        my_logger.error(f"Exporting {file_path} failed. Aborting!")
        return False
    
    my_logger.info(f"Exported zip {file_path} successfully!")  
    return True


def main(file_path: str, export_payload: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
         
    if not export_asset(file_path, export_payload, agw_connection):
        my_logger.error(f"export_asset() failed for {file_path}. Aborting deployment process!")
        print("##vso[task.complete result=Failed;]")
        return
    
    my_logger.info(f"Exporting file {file_path} was successful!")
    return
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('hostname', type=str, help='buildserver hostname')
    parser.add_argument('port', type=int, help='buildserver port')
    parser.add_argument('archive-path', type=str, help='path to the zip archive')
    parser.add_argument('export-payload', type=str, help='payload to export the asset')
    parser.add_argument('--testing', action='store_true', help='bool for testing')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    file_path = args.get('archive-path', "not declared")
    export_payload = args.get('export-payload', "not declared")
    USE_SSL: bool = not args.get('no_ssl', False)
    main(file_path, export_payload, agw_user, agw_password, hostname, port, USE_SSL)
