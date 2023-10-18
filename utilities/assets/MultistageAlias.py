from utilities.assets.Alias import Alias
from utilities.assets.AliasFactory import AliasFactory


class MultistageAlias():
    """MultistageAlias is a composition of an Alias and its staging values.
    
    :param payload: payload dict of the asset
    :param staging_values: staging_values dict with entries [dev, test, qs, prod]
    """
    
    def __init__(self, payload: dict, staging_values: dict = {}) -> None:
        if "connection_details" in list(payload.keys()):
            self.connection_details: dict = payload["connection_details"]
            new_alias = AliasFactory.create_alias(payload["alias"])
        else:
            self.connection_details: dict = staging_values
            new_alias = AliasFactory.create_alias(payload)
        
        if new_alias is None:
            raise ValueError("error in creation of MultistageAlias. Wrong alias payload provided!")
        self.alias: Alias = new_alias
        
        self.name: str = self.alias.name
        self.id: str = self.alias.id
        self.type: str = self.alias.type
        self.asset_type = "alias"
        
    def set_stage_values(self, update_dict: dict) -> None:
        self.connection_details = update_dict
        
    def set_stage_values_by_stage(self, stage: str, update_dict: dict) -> None:
        self.connection_details[stage] = update_dict
        
    def get_connection_details(self) -> dict:
        return self.connection_details
    
    def get_connection_details_by_stage(self, stage: str) -> dict:
        return self.connection_details[stage]   
        
    def get_dict(self):
        representation = {
            "alias": self.alias.get_payload(),
            "connection_details": self.connection_details
        }
        return representation
    
    def get_alias_payload(self):
        return self.alias.get_payload()
    
    def __repr__(self):
        return(f"MultistageAlias[{self.name}: {self.connection_details}]")

