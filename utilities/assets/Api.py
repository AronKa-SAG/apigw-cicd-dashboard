from utilities.assets.Asset import Asset


class Api(Asset):
    """API asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        try:
            fix_payload = payload["apiResponse"]["api"]
        except KeyError:
            fix_payload = payload
        super().__init__(fix_payload)
        self.name = fix_payload["apiName"]
        self.id = fix_payload["id"]
        self.description: str = fix_payload.get("apiDescription", "")
        self.is_active: bool = fix_payload.get("isActive", False)
        self.__tags: list = fix_payload.get("apiDefinition", {}).get("apiTags", [])
        self.__policies: list = fix_payload.get("policies", [])
        # TODO: add mocking_active bool
        self.asset_type = "apis"
        
    def add_tags(self, tags: list) -> list:
        """Add the given tags. Returns the updated variable value."""
        for tag in tags:
            if not tag in self.__tags:
                self.__tags.append(tag)
        return self.__tags    
        
    def get_tags(self) -> list:
        """Returns the list of tags."""
        return self.__tags    
    
    def get_policies(self) -> list:
        """Returns the list of policies."""
        return self.__policies 
    
    def get_payload(self) -> dict:
        """Returns the API's payload."""
        self._update_payload() 
        return self._payload

    def _update_payload(self) -> None:
        """Updates objects payload"""
        self._payload["apiName"] = self.name
        self._payload["apiDescription"] = self.description
        self._payload["isActive"] = self.is_active
        tags = []
        api_tags = []
        if self.__tags:
            for tag in self.__tags:
                tags.append({"name": tag})
                api_tags.append(tag)
    
        self._payload["apiDefinition"]["tags"] = tags
        self._payload["apiDefinition"]["apiTags"] = api_tags
        self._payload["policies"] = self.__policies
        