from utilities.assets.Api import Api


class DashboardApi():
    """API asset class for CI/CD Dashboard.
    
    Attributes: 
    name (str): name of the API
    id (str): id of the API
    """
    
    def __init__(self, api_name_version: str, api_id: str) -> None:
        self.gw_api = None
        self.name_version = api_name_version
        api_name_list = api_name_version.rsplit('[')
        self.name = api_name_list[0]
        self.version = api_name_list[1][:-1]
        self.id = api_id
        self.__app_list = []
        self.__alias_list = []
    
    def update_gw_api(self, gateway_api: Api) -> None:
        self.gw_api = gateway_api
        return
    
    def add_linked_apps(self, app_name: str) -> None:
        """Add the given app names. Returns the updated variable value."""
        self.__app_list.append(app_name)
        return
    
    def get_apps(self) -> list:
        """Returns the list of app ids."""
        return self.__app_list    
    
    def add_linked_aliases(self, alias_ids: list) -> list:
        """Add the given app ids. Returns the updated variable value."""
        for alias_id in alias_ids:
            if not alias_id in self.__alias_list:
                self.__alias_list.append(alias_id)
        return self.__alias_list
    
    def get_alias_ids(self) -> list:
        """Returns the list of app ids."""
        return self.__alias_list
    
    def __repr__(self) -> str:
        return f"API[{self.name_version}|{self.id}]"