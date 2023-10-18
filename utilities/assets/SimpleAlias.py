from utilities.assets.Alias import Alias


class SimpleAlias(Alias):
    """Simple Alias asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)        
        
        self.value: str = payload.get("value", "")

    def update_alias(self, update_dict: dict) -> None:
        """Update the alias' value(s)."""
        self.value = update_dict.get("value", "")
        
    def get_value(self) -> str:
        return self.value
    
    def get_staging_values(self) -> dict:
        return {
            "value": self.get_value()
        }
        
    def _update_payload(self) -> None:
        """Updates objects payload"""
        self._payload["name"]= self.name
        self._payload["type"] = self.type
        self._payload["value"]= self.value
    
    def __repr__(self):
        return(f"SimpleAlias[{self.name}: {self.value}]")
