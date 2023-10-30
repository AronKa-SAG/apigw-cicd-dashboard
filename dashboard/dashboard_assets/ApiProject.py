import re
from dashboard.dashboard_assets.DashboardAlias import DashboardAlias
from dashboard.dashboard_assets.DashboardApi import DashboardApi
from dashboard.dashboard_assets.DashboardApplication import DashboardApplication
from utilities.assets.Api import Api
from utilities.assets.Application import Application


class ApiProject:
    def __init__(self, project_name: str):
        self.name = project_name
        self.stages = {}
        self.apis: list[DashboardApi] = []
        self.apps: list[DashboardApplication] = []
        self.aliases: list[DashboardAlias] = []
        self.policy_actions: list = []
    
    def add_asset(self, asset_type, asset_id, asset_name):
        dict = {
            "applications": self.add_app,
            "aliases": self.add_alias,
            "apis": self.add_api,
            #"policyActions": self.add_policy_action,
        }
        return dict[asset_type]((asset_id, asset_name))
    
    def get_assets_string(self):
        apis_str = ", ".join(api.name for api in self.apis)
        apps_str = ", ".join(app.name for app in self.apps)
        alias_str = ", ".join(alias.name for alias in self.aliases)
        return f"APIs: {apis_str} \nApplications: {apps_str} \nAliases: {alias_str}"
    
    def get_api_ids(self) -> list[str]:
        return [api.id for api in self.apis]
    
    def get_number_of_apis(self) -> int:
        return len(self.apis)
    
    def get_app_ids(self) -> list[str]:
        return [app.id for app in self.apps]
    
    def get_alias_ids(self) -> list[str]:
        return [alias.id for alias in self.aliases]
    
    def get_policy_actions_ids(self) -> list[str]:
        return [policy_action.id for policy_action in self.policy_actions]
    
    def get_deployed_stages(self) -> list[str]:
        return list(self.stages.values())
    
    def add_api(self, api_tuple: tuple) -> list[DashboardApi]:
        if api_tuple[0] in self.get_api_ids():
            return self.apis
        self.apis.append(DashboardApi(api_tuple[1], api_tuple[0]))
        return self.apis
    
    def update_gateway_apis(self, gateway_apis: list[Api]):
        for api in self.apis:
            for gateway_api in gateway_apis:
                if api.id == gateway_api.id:
                    api.update_gw_api(gateway_api)
    
    def add_app(self, app_tuple: tuple) -> list[DashboardApplication]:
        if app_tuple [0] in self.get_app_ids():
            return self.apps
        self.apps.append(DashboardApplication(app_tuple[1], app_tuple[0]))
        return self.apps
    
    def update_gateway_apps(self, gateway_apps: list[Application]):
        for app in self.apps:
            for gateway_app in gateway_apps:
                if app.id == gateway_app.id:
                    app.update_gw_app(gateway_app)
                    linked_apis = gateway_app.api_list
                    for api_id in linked_apis:
                        try:
                            found_api = self.get_api_by_id(api_id)
                            found_api.add_linked_apps(app.name)
                        except KeyError:
                            print(f"Couldn't find API with ID {api_id}")
    
    def add_alias(self, alias_tuple: tuple) -> list[DashboardAlias]:
        if alias_tuple[0] in self.get_alias_ids():
            return self.aliases
        self.aliases.append(DashboardAlias(alias_tuple[1], alias_tuple[0]))
        return self.aliases
    
    # def add_policy_action(self, policy_tuple: tuple) -> list[DashboardAlias]:
    #     if policy_tuple[0] in self.get_policy_actions_ids():
    #         return self.policy_actions
    #     pattern = r'\[[A-Za-z0-9]+routing[A-Za-z0-9]+\]'
    #     if re.match(pattern, policy_tuple[1].lower()):
    #         self.policy_actions.append(DashboardAlias(policy_tuple[1], policy_tuple[0]))
    #     return self.policy_actions
    
    def get_api_by_id(self, api_id: str) -> DashboardApi:
        for api in self.apis:
            if api.id == api_id:
                return api
        raise KeyError(f"Couldn't find API with ID {api_id}")
    
    def link_aliases_and_apis(self) -> None:
        for api in self.apis:
            alias_names = []
            for alias in self.aliases:
                alias_names.append(alias.name)
                alias.add_linked_api(api.name)
            api.add_linked_aliases(alias_names)
        return
    
    def __repr__(self) -> str:
        # api_names = [api[1] for api in self.apis]
        # return f"{self.name}: {api_names}"
        return f"{self.name}: {self.apis}"