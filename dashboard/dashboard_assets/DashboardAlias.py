from utilities.assets.Alias import Alias


class DashboardAlias():
    """Alias asset class for CI/CD Dashboard.
    
    Attributes: 
    name (str): name of the Alias
    id (str): id of the Alias
    """
    
    def __init__(self, alias_name: str, alias_id: str) -> None:
        self.gw_alias = None
        self.name = alias_name
        self.id = alias_id
        self.linked_apis = []
    
    def update_gw_alias(self, gateway_alias: Alias) -> None:
        self.gw_alias = gateway_alias
        return
    
    def add_linked_api(self, api_name: str) -> None:
        self.linked_apis.append(api_name)
        return
        
    def get_linked_apis(self) -> list:
        """Returns the linked api's names value."""
        return self.linked_apis

    def __repr__(self) -> str:
        return f"Alias[{self.name}|{self.id}]"