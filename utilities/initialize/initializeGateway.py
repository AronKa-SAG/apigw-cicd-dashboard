import argparse
import logging
from pathlib import Path
import yaml
from utilities.assets.Loadbalancer import Loadbalancer
from utilities.assets.LocalAuthServer import LocalAuthServer
from utilities.assets.Proxy import Proxy
from utilities.connection.ApigwUtil import ApigwUtil

my_logger = logging.getLogger("agw-staging")


def update_proxy_config(agw_connection: ApigwUtil, hostname: str, port: int) -> bool:
    proxy_config = {
        "proxyAlias": "default_proxy",
        "host": hostname,
        "port": port,
        "username": "test",
        "password": "manage",
        "protocol": "HTTPS",
        "isDefault": "Y"
    }
    my_loadbalancer = Proxy(proxy_config)
    status_code = agw_connection.update_asset(my_loadbalancer)
    
    if status_code > 201:
        my_logger.error("Couldn't set proxy config!")
        return False
    
    my_logger.debug("Successfully updated proxy configuration!")
    return True


def update_loadbalancer_config(agw_connection: ApigwUtil, hostname: str, port: int) -> bool:
    loadbalancer_config = {
        "websocketUrls": [],
        "httpsUrls": [f"https://{hostname}:{port}"],
        "httpUrls": [f"https://{hostname}:{port}"]
    }
    my_loadbalancer = Loadbalancer(loadbalancer_config)
    status_code = agw_connection.update_asset(my_loadbalancer)
    
    if status_code > 201:
        my_logger.error("Couldn't set load balancer config!")
        return False
    
    my_logger.debug("Successfully updated loadbalancer configuration!")
    return True


def update_local_as(agw_connection: ApigwUtil, hostname: str) -> bool:
    local_as: LocalAuthServer | None = agw_connection.get_asset_by_id("alias", "local")
    if local_as is None:
        my_logger.error("Couldn't get authorization server config!")
        return False
    
    my_logger.debug(f"setting new config for local AS.")
    local_as.update_local_introspection_config(f"https://{hostname}")
    local_as.update_token_generator_config(3600, 60, 60, "RS512")
    local_as.update_ssl_config("DEFAULT_IS_KEYSTORE", "ssos")
    
    status_code = agw_connection.update_asset(local_as)
    if status_code > 201:
        my_logger.error("Couldn't update local authorization server!")
        return False
    
    my_logger.debug("Successfully updated local AS!")
    return True


def initialize_gateway(agw_connection: ApigwUtil, hostname: str, port: int, settings_dict: dict) -> None:
    if settings_dict["update_lb"]:
        if not update_loadbalancer_config(agw_connection, hostname, port):
            my_logger.error(f"update_loadbalancer_config() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
    
    if settings_dict["update_local_as"]:
        if not update_local_as(agw_connection, hostname):
            my_logger.error(f"update_local_as() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
        
    if settings_dict["update_proxy"]:
        if not update_proxy_config(agw_connection, hostname, port):
            my_logger.error(f"update_proxy_config() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            return
    
    my_logger.info(f"Intializing build gateway was successful!")
    return


def main(workspace: str, target_environment_config: str, agw_user: str, agw_password: str, hostname: str, port: int, use_ssl: bool):
    agw_connection = ApigwUtil(hostname, port, use_ssl, agw_user, agw_password)
        
    settings_file = Path(f"{workspace}/configuration/{target_environment_config}")
    settings_dict = {"update_lb": True, "update_local_as": True, "update_proxy": True}
    if settings_file.exists():
        with settings_file.open() as file:
            settings = yaml.safe_load(file)
        try:    
            settings_dict.update(settings["initialize"])
        except KeyError:
            my_logger.info(f"'initialize' not set in {settings_file}. Using default values.")
        
    initialize_gateway(agw_connection, hostname, port, settings_dict)
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI arguments')
    parser.add_argument('workspace', type=str, help='path of the workspace')
    parser.add_argument('target-env', type=str, help='target AGW env')
    parser.add_argument('agw-user', type=str, help='API Gateway import user')
    parser.add_argument('agw-password', type=str, help='API Gateway import user password')
    parser.add_argument('hostname', type=str, help='buildserver hostname')
    parser.add_argument('port', type=int, help='buildserver port')
    parser.add_argument('--testing', action='store_true', help='bool for testing')
    parser.add_argument('--no-ssl', action='store_true', help='flag for not using ssl connection')

    args = vars(parser.parse_args())
    workspace = args.get('workspace', "not declared")
    target_env_config = args.get('target-env', "not declared")
    agw_user = args.get('agw-user', "not declared")
    agw_password = args.get('agw-password', "not declared")
    hostname = args.get('hostname', "not declared")
    port = args.get('port', -1)
    USE_SSL: bool = not args.get('no_ssl', False)
    main(workspace, target_env_config, agw_user, agw_password, hostname, port, USE_SSL)
