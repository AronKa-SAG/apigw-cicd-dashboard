from typing import TypeVar
from utilities.assets.Alias import Alias
from utilities.assets.AliasFactory import AliasFactory
from utilities.assets.Api import Api
from utilities.assets.GatewayScope import GatewayScope
from utilities.assets.Policy import Policy
from utilities.assets.Application import Application
from utilities.assets.EndpointAlias import EndpointAlias
from utilities.assets.LocalAuthServer import LocalAuthServer
from utilities.assets.SimpleAlias import SimpleAlias

A = TypeVar("A", Alias, Api, Policy, Application, LocalAuthServer, GatewayScope)


class AssetFactory():
    """Factory class for all assets.
    
    :param payload: payload dict of the alias
    """

    @classmethod
    def create_asset_by_type(cls, response_json: dict, asset_type: str) -> A:
        dict = {
            "applications": Application,
            "Application": Application,
            "apis": Api,
            "API": Api,
            "alias": LocalAuthServer,
            "Alias": AliasFactory.create_alias,
            "GatewayScope": GatewayScope            
        }
        return dict[asset_type](response_json)
    
    @classmethod
    def create_assets(cls, response_json: dict, asset_type: str) -> list[A]:
        dict = {
            "applications": cls.parse_applications,
            "policyActions": cls.parse_policies,
            "alias": cls.parse_aliases,
            "scopes": cls.parse_gateway_scopes,
            "apis": cls.parse_apis,
        }
        return dict[asset_type](response_json)
    
    @classmethod    
    def parse_apis(cls, response_json: dict) -> list[Api]:
        if not response_json.get("apiResponse", None):
            return []

        return [Api(api_payload["api"]) for api_payload in response_json["apiResponse"]]
    
    @classmethod    
    def parse_applications(cls, response_json: dict) -> list[Application]:
        if len(response_json.get("applications", -1)) == 0:
            return []
        if not response_json.get("applications", None):
            return []

        return [Application(app_payload) for app_payload in response_json["applications"]]

    @classmethod    
    def parse_policies(cls, response_json: dict) -> list[Policy]:
        if not response_json.get("policyAction", None):
            return []
        
        return [Policy(policy_payload) for policy_payload in response_json["policyAction"]]
    
    @classmethod    
    def parse_gateway_scopes(cls, response_json: dict):
        if not response_json.get("scopes", None):
            return []
        
        return [GatewayScope(gatewayscopes_payload) for gatewayscopes_payload in response_json["scopes"]]
    
    @classmethod    
    def parse_aliases(cls, response_json: dict) -> list[type[Alias]]:
        if not response_json.get("alias", None):
            return []
        
        alias_list = []
        for alias_payload in response_json["alias"]:
            new_alias = AliasFactory.create_alias(alias_payload)
            if new_alias:
                alias_list.append(new_alias)
        return alias_list
