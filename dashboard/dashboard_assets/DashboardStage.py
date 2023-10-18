import sys
from dashboard.dashboard_assets.ApiProject import ApiProject
from utilities.assets.Alias import Alias
from utilities.assets.Api import Api
from utilities.assets.Application import Application


class DashboardStage():
    """
    Stage holding data which represent asset on the stage.
    """
    
    def __init__(self, stage_name: str, asset_list: list[str], projects: list[ApiProject] = [], apis = [], apps = [], aliases = []) -> None:
        self.name = stage_name
        self.projects: list[ApiProject] = projects
        self.apis = apis
        self.apps = apps
        self.aliases = aliases
        self.synched = { asset: False for asset in asset_list }
    
    def add_project(self, project: ApiProject):
        if project in self.projects:
            return self.projects
        self.projects.append(project)
        return self.projects
    
    def set_assets(self, asset_type: str, asset_list):
        # print(f"setting {asset_type} with {asset_list}", file=sys.stdout)
        match asset_type:
            case "apis":
                self.apis = asset_list
                # print(f"setting {self.apis}", file=sys.stdout) 
            case "alias":
                self.aliases = asset_list
                # print(f"setting {self.aliases}", file=sys.stdout)
            case "applications":
                self.apps = asset_list
                # print(f"setting {self.apps}", file=sys.stdout)
        self.synched[asset_type] = True
        
    def get_assets(self, asset_type: str) -> list:
        match asset_type:
            case "apis":
                return self.apis
            case "alias":
                return self.aliases
            case "applications":
                return self.apps
        return []
    
    def __repr__(self) -> str:
        return f"{self.name}"