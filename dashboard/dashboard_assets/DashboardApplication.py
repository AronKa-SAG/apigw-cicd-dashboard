from utilities.assets.Application import Application


class DashboardApplication():
    """Application asset class for CI/CD Dashboard.
    
    Attributes: 
    name (str): name of the Application
    id (str): id of the Application
    """
    
    def __init__(self, app_name: str, app_id: str) -> None:
        self.gw_app = None
        self.name = app_name
        self.id = app_id
    
    def update_gw_app(self, gateway_app: Application) -> None:
        self.gw_app = gateway_app
        return
    
    def get_linked_apis(self) -> list:
        """Returns the linked api's ids value."""
        if self.gw_app:
            return self.gw_app.api_list
        return []

    def __repr__(self) -> str:
        return f"APP[{self.name}|{self.id}]"