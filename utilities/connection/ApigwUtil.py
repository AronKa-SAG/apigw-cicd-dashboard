import copy
import json
import logging
from typing import List, TypeVar
from requests.auth import HTTPBasicAuth
import requests
import urllib3
from utilities.assets.Alias import Alias
from utilities.assets.Api import Api
from utilities.assets.Application import Application
from utilities.assets.Asset import Asset
from utilities.assets.AssetFactory import AssetFactory
from utilities.assets.GatewayScope import GatewayScope
from utilities.assets.LocalAuthServer import LocalAuthServer
from utilities.assets.Policy import Policy

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore
A = TypeVar("A", Alias, Api, Policy, Application, LocalAuthServer, GatewayScope)
my_logger = logging.getLogger("agw-staging")


class ApigwUtil:
    """Wrapper around the API Gateway Admin Rest API.
    
    :param hostname: hostname of the AGW to connect to.
    :param port: port of the AGW to connect to.
    :param agw_user: name of import-user for basic authentication.
    :param agw_password: password of import-user for basic authentication.
    """
    
    proxies = { }
    
    def __init__(self, hostname: str = "localhost", port: int = 5555, ssl_connection: bool = False, agw_user: str = "Administrator", agw_password: str = "manage") -> None:
        protocol = "http"
        if ssl_connection:
            protocol = "https"
        self.base_url = f"{protocol}://{hostname}:{port}/rest/apigateway"
        self.basic_auth = HTTPBasicAuth(agw_user, agw_password)
        self.header = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if not self.health_check():
            my_logger.error(f"health_check() failed. Aborting deployment process!")
            print("##vso[task.complete result=Failed;]")
            raise RuntimeError(f"Couldn't establish connection to API Gateway. Connection details: {self.base_url}/health")
        
    def health_check(self) -> bool:
        """Call health endpoint of the API Gateway. Returns true or false."""
        url = f"{self.base_url}/health"
        try:
            request = requests.get(url, proxies=self.proxies, verify=False)
        except requests.exceptions.ConnectionError:
            my_logger.warning(f"health check call Failed. Couldn't establish connection to API Gateway.")
            return False
        if request.status_code > 200:
            my_logger.warning(f"health check Failed with status: {request.status_code}.")
            return False
        return True
    
    def api_set_active(self, api: Asset, state_active: bool) -> int:
        """Activates the given API. Returns the HTTP status code."""
        url = f"{self.base_url}/apis/{api.id}/"
        if state_active:
            url += "activate"
        else:
            url += "deactivate"
        request = requests.put(url, headers=self.header, auth=self.basic_auth, proxies=self.proxies, verify=False)
        
        if request.status_code > 201:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)    
            
        return request.status_code
    
    def activate_application(self, app: Asset) -> int:
        """Activates the given App. Returns the HTTP status code."""
        url = f"{self.base_url}/applications/{app.id}"
        payload = { 
            "isSuspended": False
        }
        payload_str = json.dumps(payload)
        request = requests.patch(url, headers=self.header, auth=self.basic_auth, data=payload_str, proxies=self.proxies, verify=False)
        
        if request.status_code > 201:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)    
            
        return request.status_code
    
    def create_asset(self, asset: Asset) -> int:
        """Creates the given asset. Returns the HTTP status code."""
        url = f"{self.base_url}/{asset.asset_type}"
        payload_str = json.dumps(asset.get_payload())
        request = requests.post(url, headers=self.header, auth=self.basic_auth, data=payload_str, proxies=self.proxies, verify=False)
        
        if request.status_code == 400:
            my_logger.debug(asset.get_payload())
            
        if request.status_code > 201:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content) 
            
        return request.status_code

    def update_asset(self, asset: Asset) -> int:
        """Updates the given asset. Returns the HTTP status code."""
        url = f"{self.base_url}/{asset.asset_type}/{asset.id}"
        payload_str = json.dumps(asset.get_payload())
        request = requests.put(url, headers=self.header, auth=self.basic_auth, data=payload_str, proxies=self.proxies, verify=False)
        
        if request.status_code == 400:
            my_logger.debug(asset.get_payload())
        
        if request.status_code > 201:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)    
            
        return request.status_code
        
    def delete_asset(self, asset: Asset) -> int:
        """Deletes the given asset. Returns the HTTP status code."""
        url = f"{self.base_url}/{asset.asset_type}/{asset.id}"
        my_logger.debug(f"DELETE /{asset.asset_type} - {self.header} - {self.proxies} ")
        request = requests.delete(url, headers=self.header, auth=self.basic_auth, proxies=self.proxies, verify=False)
        
        if request.status_code > 204:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)
            
        return request.status_code
    
    def delete_asset_by_id(self, asset_type: str, asset_id: str) -> int:
        """Deletes the given asset. Returns the HTTP status code."""
        url = f"{self.base_url}/{asset_type}/{asset_id}"
        my_logger.debug(f"DELETE /{asset_type} - {self.header} - {self.proxies} ")
        request = requests.delete(url, headers=self.header, auth=self.basic_auth, proxies=self.proxies, verify=False)
        
        if request.status_code > 204:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)
            
        return request.status_code

    def get_assets(self, asset_type: str, api_details: bool = True) -> list[A]:
        """Returns all assets of asset_type"""
        url = f"{self.base_url}/{asset_type}"
        my_logger.debug(f"GET /{asset_type} - {self.header} - {self.proxies} ")
        request = requests.get(url, headers=self.header, auth=self.basic_auth, proxies=self.proxies, verify=False)
        
        if request.status_code > 200:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            raise ConnectionError(f"Couldn't retrieve {asset_type} from api gateway {url}. \n", 
                                    f"Response status code: {request.status_code} \n",
                                    f"Response content: {request.content}")
        
        # work around for different GET /apis payload
        if api_details and asset_type == "apis":
            if request.json()["apiResponse"][0].get("responseStatus", "") == "NOT_FOUND":
                my_logger.warning("no apis found!")
                return []
            found_apis = []
            for api_payload in request.json()["apiResponse"]:
                my_api = self.get_asset_by_id("apis", api_payload.get("api").get("id"))
                found_apis.append(my_api)
            return found_apis
        else:
            asset_list = AssetFactory.create_assets(request.json(), asset_type)
            if not asset_list:
                my_logger.warning(f"No {asset_type} found on {url}!")
        return asset_list
    
    def get_asset_by_id(self, asset_type: str, id: str) -> A | None:
        """Returns specific asset by id."""
        url = f"{self.base_url}/{asset_type}/{id}"
        my_logger.debug(f"GET /{asset_type} - {self.header} - {self.proxies} ")
        request = requests.get(url, headers=self.header, auth=self.basic_auth, proxies=self.proxies, verify=False)
        
        if request.status_code > 200:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content) 
            return None

        created_asset = AssetFactory.create_asset_by_type(request.json(), asset_type)
        return created_asset
    
    def get_asset_by_name(self, asset_type: str, name: str) -> dict:
        """Returns specific asset by name."""
        url = f"{self.base_url}/search"
        my_logger.debug(f"POST /search - {self.header} - {self.proxies} ")
        attribute_name_map = {
            "api": "apiName"
        }
        payload_json = {
            "types": [asset_type],
            "scope": [
                {
                    "attributeName": attribute_name_map.get(asset_type, "name"),
                    "keyword": name
                }
            ]
        }
        payload_str = json.dumps(payload_json)
        request = requests.post(url, headers=self.header, auth=self.basic_auth, data=payload_str, proxies=self.proxies, verify=False)
        
        if request.status_code > 200:
            my_logger.warning(f"request: {url} with status: {request.status_code}")
            my_logger.debug(request.content) 
            return {}       
            
        return request.json()
        
    def import_asset(self, file_path: str, overwrite_params: List[str], preserve_state: bool = True) -> int:
        """Imports zip archive. Returns the HTTP status code."""
        url = f"{self.base_url}/archive?overwrite={','.join(overwrite_params)}"
        if not preserve_state:
            url += "&preserveAssetState=false"
        my_logger.debug(url)
        header = copy.deepcopy(self.header)
        header["Content-Type"] = "application/octet-stream"
        asset_name = file_path
        if '/' in file_path:
            asset_name = file_path.rsplit("/", 1)[1]
        with open(file_path,'rb') as file_payload:
            request = requests.post(url, headers=header, auth=self.basic_auth, data=file_payload, proxies=self.proxies, verify=False)
        if request.status_code > 201:
            my_logger.error(f"Importing asset {asset_name} failed! request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)
        else:
            my_logger.debug(f"Importing asset {asset_name}: \ncontent: {request.content} \nheaders: {request.headers}")
            # work-around for bug in the admin rest api
            for result in request.json()["ArchiveResult"]:
                if list(result.keys())[0] != "API":
                    continue
                info = list(result.values())[0]
                if info["status"] == "Failed":
                    request.status_code = 400
                    my_logger.error(f"Importing {result.keys()} of asset {asset_name} failed! Set status code to 400.") 
                    break
        return request.status_code


    def export_asset(self, file_path: str, payload_path: str) -> int:
        url = f"{self.base_url}/archive"
        my_logger.debug(url)
        header = copy.deepcopy(self.header)
        header["x-HTTP-Method-Override"] = "GET"
        asset_name = file_path
        if '/' in file_path:
            asset_name = file_path.rsplit("/", 1)[1]

        with open(payload_path, 'r') as file_payload:
            json_payload = json.load(file_payload)
            payload = json.dumps(json_payload)
            request = requests.post(url, headers=header, auth=self.basic_auth, data=payload, proxies=self.proxies, verify=False)
            
        if request.status_code > 201:
            my_logger.error(f"Exporting asset to {asset_name} failed! request: {url} with status: {request.status_code}")
            my_logger.debug(request.content)
            return request.status_code
        
        with open(file_path, 'wb') as zip:
            zip.write(request.content)

        return request.status_code
