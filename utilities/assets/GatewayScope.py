from utilities.assets.Asset import Asset


class GatewayScope(Asset):
    """GatewayScope asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.name = payload["scopeName"]
        self.id: str = payload["id"]
        self.description: str = payload["scopeDescription"]
        self.api_scopes: list[str] = payload.get("apiScopes", [])
        self.required_auth_scopes: dict = payload.get("requiredAuthScopes", [])
        self.asset_type = "scopes"
        
    def _update_payload(self) -> None:
        """Updates objects payload"""
        self._payload["scopeName"] = self.name
        self._payload["apiScopes"] = self.api_scopes
        self._payload["requiredAuthScopes"] = self.required_auth_scopes
        self._payload["scopeDescription"] = self.description
    
    def references_apis(self, api_id: str) -> bool:
        """Returns True if api_id is referenced in the api_scopes list.
        
        :param api_id: either api_id as a string or multiple ids comma-separated.
        """    
        for id in api_id.split(','):
            if id in self.api_scopes:
                return True
        return False