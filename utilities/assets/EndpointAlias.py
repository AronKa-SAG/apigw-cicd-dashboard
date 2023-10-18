from utilities.assets.Alias import Alias


class EndpointAlias(Alias):
    """Endpoint Alias asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.endpoint: str = payload.get("endPointURI", "")
        self.keystore_alias: str = payload.get("keystoreAlias", "")
        self.key_alias: str = payload.get("keyAlias", "")
        self.truststore_alias: str = payload.get("truststoreAlias", "")
        
    def update_alias(self, update_dict: dict) -> None:
        """Update the alias' value(s)."""
        self.endpoint = update_dict.get("endPointURI", "")
        self.keystore_alias = update_dict.get("keystoreAlias", "")
        self.key_alias = update_dict.get("keyAlias", "")
        self.truststore_alias = update_dict.get("truststoreAlias", "")
        
    def get_value(self) -> str:
        return self.endpoint
    
    def get_staging_values(self) -> dict:
        return {
            "endPointURI": self.endpoint,
            "keystoreAlias": self.keystore_alias,
            "keyAlias": self.key_alias,
            "truststoreAlias": self.truststore_alias
        }
        
    def _update_payload(self) -> None:
        """Updates objects payload."""
        self._payload["name"]= self.name
        self._payload["endPointURI"]= self.endpoint
        self._payload["keystoreAlias"]= self.keystore_alias
        self._payload["keyAlias"]= self.key_alias
        self._payload["truststoreAlias"]= self.truststore_alias
    
    def __repr__(self):
        return(f"EndpointAlias[{self.name}: {self.endpoint}, {self.keystore_alias}, {self.key_alias}, {self.truststore_alias}]")
