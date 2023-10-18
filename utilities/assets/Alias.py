from utilities.assets.Asset import Asset
from abc import abstractmethod


class Alias(Asset):
    """Abstract alias asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.name = payload["name"]
        self.id = payload["id"]
        self.type: str = payload["type"]
        
        self.asset_type = "alias"
    
    @abstractmethod  
    def update_alias(self, update_dict: dict) -> None:
        """Update the alias' value(s)."""
        pass
    
    @abstractmethod  
    def get_value(self) -> str:
        """Returns the alias' main value."""
        pass
    
    @abstractmethod  
    def get_staging_values(self) -> dict:
        """Returns the alias' staging values."""
        pass
    
    @abstractmethod    
    def _update_payload(self) -> None:
        """Updates objects payload."""
        pass
            
    def __repr__(self):
        return(f"Alias[{self.name}: {self.get_staging_values}]")