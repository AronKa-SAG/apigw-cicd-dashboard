import os
import json
from pathlib import Path
import sys
import yaml
import git
from dashboard.dashboard_assets.ApiProject import ApiProject
from dashboard.dashboard_assets.DashboardApi import DashboardApi
from utilities.assets.Asset import Asset
from utilities.connection.ApigwUtil import ApigwUtil
from dashboard.dashboard_assets.DashboardStage import DashboardStage

asset_type_mapping = {
    "API": "apis",
    "Application": "applications",
    "Alias": "aliases"
}

config_path = f"{Path().absolute()}/dashboard/configuration/dashboard_config.yaml"

class ApigwData:
    """Dataclass containing project, api, app and alias information for each stage.
    
    :param hostname: hostname of the AGW to connect to.
    :param port: port of the AGW to connect to.
    :param agw_user: name of import-user for basic authentication.
    :param agw_password: password of import-user for basic authentication.
    """
    stages: list[DashboardStage] = []
    asset_list = ["apis", "applications", "alias"]
    SORT_ORDER = {"DEV": 0, "TEST": 1, "QS": 2, "PROD": 3}
    
    
    def __init__(self) -> None:
        self.load_configuration(Path(config_path))
        self.__work_dir: str = self.clone_git_repo(Path().absolute()/"data-repo")
        # self.apigw_connection = ApigwUtil(hostname, port, ssl_connection, agw_user, agw_password)
        self.stages_config_dict = self.__get_stage_configs()
        self.stages = [DashboardStage(stage_name, self.asset_list) for stage_name in self.stages_config_dict.keys()]
        self.assets_on_stages = { stage.name: { asset: [] for asset in self.asset_list } for stage in self.stages}
        # assets_on_stages: {'Config': {'apis': [apis[ name: Common_PostmanEcho --- id: 0245c29f-e583-4ebd-824a-a4762ad85fbf ], 
        #                                        apis[ name: NumberConversion --- id: 211d57cf-dae3-4fbc-9836-c27b3c7f8182 ], 
        #                                        apis[ name: Petstore_BasicAuth --- id: 131ee26d-056a-432b-b30d-5e6ec4bb4a6a ]
        #                                       ], 
        #                               'applications': [], 
        #                               'aliases': []
        #                               },
        #self.asset_sync = { stage.name: { asset: False for asset in self.asset_list } for stage in self.stages}
        self.projects_list = self.__get_projects_from_repo()
        # projects_list: [demo-alias-value-retention: [('ffd2bf1e-7d49-46a9-8278-a7d91a70d313', 'PostmanEcho_Alias[1.0]')], 
        #                 demo-alias-value-substitution: [('7cad685d-646e-4cc5-819e-ac36b01e2c7c', 'SimpleDemoApi_Alias[1.0]')], 
        #                 demo-api-tests: [('d73d5702-6925-41a0-8c23-933326c27b96', 'PostmanEcho[1.0]')], 
        #                 demo-application-export-disabled: [('4ceba5ec-f0bc-42c7-a431-40ec951aeecf', 'PostmanEcho_OAuth2[1.0]')], 
        #                 demo-failing-api-tests: [('d73d5702-6925-41a0-8c23-933326c27b96', 'PostmanEcho[1.0]')], 
        #                 demo-four-applications: [('75d996f2-c368-4241-b930-2550b791903d', 'FourApplications[1.0]')], 
        #                 demo-illegal-application-name: [('70ea3b13-db96-434b-88a8-424bf853233d', 'IllegalApplicationName[1.0]')], 
        #                 demo-illegal-policy: [('c52931ab-e137-48b5-8041-029a72a9aa2b', 'IllegalPolicy[1.0]')], 
        #                 demo-oauth2-scope-mappings: [('4ceba5ec-f0bc-42c7-a431-40ec951aeecf', 'PostmanEcho_OAuth2[1.0]')], 
        #                 demo-two-versions-two-aliases: [('fba9e6b8-02c1-412e-8b9e-c75d82ed836c', 'TwoVersions_TwoAliases[2.0]'), ('b437f84e-0f23-4f75-9ace-3da85c3ae73b', 'TwoVersions_TwoAliases[1.0]')]]
        self.__set_project_stages()
    
    def load_configuration(self, config_path: Path) -> None:
        if not config_path.is_file:
            raise FileNotFoundError(f"Config file {config_path.absolute()} could not be found")
        
        with config_path.open("r") as file:
            config = yaml.safe_load(file)
        
        self.__use_ssl = config.get("apigw", None).get("use_ssl", True)
        self.__username = config.get("apigw", None).get("username", "Administrator")
        self.__userpw = config.get("apigw", None).get("userpw", "manage")
        self.__github_user = config.get("git", None).get("user", "Not Set!")
        self.__github_access_token = config.get("git", None).get("accessToken", "Not Set!")
        self.__repo_url = config.get("git", None).get("repoLink", "Not Set!")
        return
    
    def clone_git_repo(self, dest_folder: str):
        """
            dest_folder(str): full path /opt/repo
            returns repository working directory
        """
        # url_string = f"https://{self.__github_user}:{self.__github_access_token}@{self.__repo_url}"
        if Path(dest_folder).exists():
            print(f"folder exists: {dest_folder}")
            return dest_folder
        os.environ['GIT_USERNAME'] = self.__github_user
        os.environ['GIT_PASSWORD'] = self.__github_access_token
        my_repo = git.Repo.clone_from(self.__repo_url, dest_folder)
        return my_repo.working_dir

    def __set_project_stages(self):
        # print(self.stages, file=sys.stdout)
        for project in self.projects_list:
            for stage in self.stages:
                project.stages[stage.name] = self.__check_project_on_stage(project, stage)
    
    def __get_stage_configs(self) -> dict:
        # env configs: configuration\*_environment.yaml
        env_config_dict = { }
        config_path: Path = Path(f"{self.__work_dir}/configuration")
        print(config_path.absolute(), file=sys.stdout)
        config_glob = list(config_path.glob(f"*_environment.yaml"))
        # print(f"found configs: {config_glob}", file=sys.stdout)
        for config_file in config_glob:
            with config_file.open() as file:
                config = yaml.safe_load(file)
            # print(config, file=sys.stdout)
            if config.get("connection", None).get("type", "disabled") != "disabled":
                env_config_dict[config.get("connection").get("alias")] = config.get("connection")
        env_config_dict = dict(sorted(env_config_dict.items(), key=lambda x:self.SORT_ORDER[x[1].get("type")]))
        # print(f"config dict: {env_config_dict}", file=sys.stdout)
        return env_config_dict
    
    def __get_projects_from_repo(self) -> list[ApiProject]:
        projects_list = []
        asset_path: Path = Path(f"{self.__work_dir}/apis")
        print(asset_path.absolute(), file=sys.stdout)
        project_glob = list(asset_path.glob(f"demo-*"))
        # print(f"found projects: {project_glob}", file=sys.stdout)
        for project in project_glob:
            project_name = str(project).rsplit("/", 1)[1]
            new_project = ApiProject(project_name)
            export_report = project / "assets/ExportReport.json"
            with export_report.open() as file:
                report = json.load(file)
            for asset in report:
                # print(asset, file=sys.stdout)
                asset_type = asset.get("assetType")
                if asset_type_mapping.get(asset_type, False):
                    asset_id = asset.get("assetObject").get("id")
                    asset_name = asset.get("assetObject").get("name")
                    new_project.add_asset(asset_type_mapping[asset_type], asset_id, asset_name)
            projects_list.append(new_project)
        return projects_list
    
    def __check_project_on_stage(self, project: ApiProject, stage: DashboardStage):
        # print("retrieve current assets", file=sys.stdout)
        apis_on_gateway = self.__get_current_assets("apis", stage)
        apps_on_gateway = self.__get_current_assets("applications", stage)
        aliases_on_gateway = self.__get_current_assets("alias", stage)
        if self.__check_api_ids(project.apis, apis_on_gateway): #and self.check_apps(project.apps, apps_on_gateway) and self.check_aliases(project.aliases, aliases_on_gateway):
            stage.add_project(project)
            project.update_gateway_apis(apis_on_gateway)
            project.update_gateway_apps(apps_on_gateway)
            return True
            # print(f"project {project.name} has apis {project.apis}")
        return False
    
    def __check_api_ids(self, apis_from_project: list[DashboardApi], apis_from_gateway: list) -> bool:
        if not apis_from_project:
            return False
        if not apis_from_gateway:
            return False
        api_ids_from_gateway = set(api.id for api in apis_from_gateway)
        api_ids_from_project = set(api.id for api in apis_from_project)
        difference_set = set(api_ids_from_project) - set(api_ids_from_gateway)
        if len(difference_set) == 0:
            return True
        else:
            return False
    
    def __get_current_assets(self, asset_type: str, stage: DashboardStage):
        # print(f"sync status {stage.name} - {asset_type}: {stage.synched[asset_type]}.", file=sys.stdout)
        # cache for assets on gateway instance
        if stage.synched[asset_type]:
            return stage.get_assets(asset_type)
        
        asset_list = self.__get_assets_from_gateway(asset_type, stage.name)
        stage.set_assets(asset_type, asset_list)
        # print(f"Asset Sync Dict:\n{self.asset_sync}.", file=sys.stdout)
        
        #print(f"GW {stage.name} | {asset_type}: {asset_list}", file=sys.stdout)
        #print(f"DashbStage {stage.name} | {stage.get_assets(asset_type)}", file=sys.stdout)
        return stage.get_assets(asset_type)
    
    def __get_assets_from_gateway(self, asset_type: str, stage: str):
        hostname = self.stages_config_dict.get(stage, {})["hostname"]
        port = self.stages_config_dict.get(stage, {})["port"]
        try:
            apigw_connection = ApigwUtil(hostname, port, self.__use_ssl, self.__username, self.__userpw)
            asset_list = apigw_connection.get_assets(asset_type, api_details=False)
        except RuntimeError:
            print(f"Couldn't connect to stage {stage}. Setting asset_list empty.", file=sys.stdout)
            asset_list = []
            print(f"error: no assets of type {asset_type} found on stage {stage}.", file=sys.stdout)
        except ConnectionError:
            print(f"Couldn't connect to stage {stage}. Setting asset_list empty.", file=sys.stdout)
            asset_list = []
            print(f"error: no assets of type {asset_type} found on stage {stage}.", file=sys.stdout)
        # print(f"{asset_type} on gw: {asset_list}", file=sys.stdout)
        return asset_list
    
    def get_apis_per_stage(self) -> list[tuple]:
        # apis_stage_tuples = [ ((apiId1, apiName1), (true, [appNames, ...]), false, (true, [appNames, ...]), false), ...]
        api_stage_tuples = []
        for project in self.projects_list:
            project_stages_tuple = project.get_deployed_stages()
            #print(project_stages_tuple, file=sys.stdout)
            for api in project.apis:
                #print(f"{api}", file=sys.stdout)
                api_stage_tuples.append(tuple([(api.id, api.name_version)] + project_stages_tuple))
        #print(api_stage_tuples, file=sys.stdout)
        # updated_api_stage_tuples = []
        # for tuple_api in api_stage_tuples:
        #     api_as_list = list(tuple_api)
        #     for i in range(1, len(api_as_list)):
        #         if api_as_list[i]:
        #             apps_using_api_list = []
        #             # print(f"for condition: {self.assets_on_stages[self.stages[i]]}", file=sys.stdout)
        #             for gw_app in self.stages[i - 1].apps:
        #                 # print(f"gateway app check: {gw_app}", file=sys.stdout)
        #                 if api_as_list[0][0] in gw_app.api_list:
        #                     # print(f"gateway app api list: {gw_app.api_list}", file=sys.stdout)
        #                     apps_using_api_list.append(gw_app.name)
        #             api_as_list[i] = (True, sorted(apps_using_api_list))
        #         else:
        #             api_as_list[i] = (False, "")
        #     api_tuple = tuple(api_as_list)
        #     updated_api_stage_tuples.append(api_tuple)     
        # # print(f"{apis_stage_tuples}", file=sys.stdout)
        return api_stage_tuples
    
    def get_apps_per_stage(self) -> list[tuple]:
        # apps_stage_tuples = [ ((apiId1, apiName1), (true, [apiNames, ...]), false,  (true, [apiNames, ...]), false), (appname2,  (true, [apiNames, ...]), false,  (true, [apiNames, ...]), false), ...]
        apps_stage_tuples = []
        for project in self.projects_list:
            project_stages = project.get_deployed_stages()
            for app in project.apps:
                app_bools = []
                for project_bool, stage in zip(project_stages, self.stages):
                    if project_bool and (stage.name in app.name):
                        app_bools.append(True)
                    else:
                        app_bools.append(False)
                apps_stage_tuples.append(tuple([(app.id, app.name)] + app_bools))
        return apps_stage_tuples
    
    def get_aliases_per_stage(self) -> list[tuple]:
        # aliases_stage_tuples = [ (aliasname1, true, false, true, false), (aliasname2, true, false, true, false), ...]
        aliases_stage_tuples = []
        for project in self.projects_list:
            project_stages_tuple = project.get_deployed_stages()
            for alias in project.aliases:
                aliases_stage_tuples.append(tuple([(alias.id, alias.name)] + project_stages_tuple))
        
        updated_aliases_stage_tuples = []
        for alias in aliases_stage_tuples:
            alias_as_list = list(alias)
            for i in range(1, len(alias_as_list)):
                if alias_as_list[i]:
                    alias_value_on_stage = "fetching alias value failed!"
                    # print(f"for condition: {self.assets_on_stages[self.stages[i]]}", file=sys.stdout)
                    for gw_alias in self.stages[i - 1].aliases:
                        # print(f"gateway alias check: {gw_alias}", file=sys.stdout)
                        if gw_alias.name == alias_as_list[0][1]:
                            alias_value_on_stage = gw_alias.get_value()
                            break
                    alias_as_list[i] = (True, alias_value_on_stage)
                else:
                    alias_as_list[i] = (False, "")
            alias = tuple(alias_as_list)
            updated_aliases_stage_tuples.append(alias)
        # print(f"{updated_aliases_stage_tuples}", file=sys.stdout)
        return updated_aliases_stage_tuples
    
    def get_projects_per_stage(self) -> list[tuple]:
        # project_tuples = [ (projectname1, project1AssetString, true, false, true, false), (projectname2, project2AssetString, true, false, true, false), ...]
        project_tuples = []
        for project in self.projects_list:
            project_stages_bool = list(project.stages.values())
            project_tuples.append(tuple([project.name, project.get_assets_string()] + project_stages_bool))
        return project_tuples
    
    def refresh_all_stages(self) -> None:
        print(f"deleting old stage information", file=sys.stdout)
        self.stages = [DashboardStage(stage_name, self.asset_list) for stage_name in self.stages_config_dict.keys()]
        self.assets_on_stages = { stage: { asset: [] for asset in self.asset_list } for stage in self.stages}
        self.asset_sync = { stage: { asset: False for asset in self.asset_list } for stage in self.stages}
        
        print(f"starting to refresh all stages", file=sys.stdout)
        for stage in self.stages:
            if stage not in self.stages:
                self.assets_on_stages[stage] = {"Error": [f"Couldn't connect to stage {stage}."] }
                continue
            for asset_type in self.asset_list:
                self.assets_on_stages[stage][asset_type] = self.__get_assets_from_gateway(asset_type, stage.name)
            print(f"{stage} done", file=sys.stdout)
        self.__set_project_stages()

    def get_api_info(self, api_id) -> list:
        # (appname1, (true, [apiNames, ...]), false,  (true, [apiNames, ...]), false)
        api_name_version = "not found"
        api_name = "not found"
        api_version = "not found"
        deployed_stages = []
        apps_using_api_list = []
        associated_project = "not found"
        associated_apps = "not found"
        
        for project in self.projects_list:
            project_stages = project.get_deployed_stages()
            for api in project.apis:
                if api.id == api_id:
                    deployed_stages = [self.stages[i] for i in range(len(project_stages)) if project_stages[i]]
                    associated_project = project.name
                    api_name_version = api.name_version
                    api_name = api.name
                    api_version = api.version
                    apps_using_api_list = api.get_apps()
                    print(f"API {api.name} with Apps {apps_using_api_list}", file=sys.stdout)
                    if len(apps_using_api_list) > 0:
                        associated_apps = ",".join(apps_using_api_list)
                    continue
        deployed_stages = ",".join([stage.name for stage in deployed_stages]) if len(deployed_stages) > 0 else "not found" 
        # print(api_modal_structure, file=sys.stdout)
        return [api_name_version, api_name, api_version, api_id, deployed_stages, associated_project, associated_apps]
    
    def get_app_info(self, app_id) -> list:
        app_name = "not found"
        associated_project = "not found"
        associated_apis = "not found"
        deployed_stages = []
        associated_apis_ids = []
        
        for project in self.projects_list:
            project_stages = project.get_deployed_stages()
            for app in project.apps:
                if app.id == app_id:
                    deployed_stages = [self.stages[i] for i in range(len(project_stages)) if project_stages[i] and self.stages[i].name in app.name]
                    app_name = app.name
                    associated_project = project.name
                    associated_apis_ids = app.get_linked_apis()
                    if len(associated_apis_ids) > 0:
                        associated_apis_list = [api.name_version for api in project.apis if api.id in associated_apis_ids]
                        associated_apis = ",".join(associated_apis_list)
        deployed_stages_string = ",".join([stage.name for stage in deployed_stages]) if len(deployed_stages) > 0 else "not found" 
        return [app_name, app_id, deployed_stages_string, associated_project, associated_apis]
    
    def get_alias_info(self, alias_id) -> list:
        alias_name = "not found"
        associated_project = "not found"
        associated_apis = "not found"
        deployed_stages = []
        
        for project in self.projects_list:
            project_stages = list(project.stages.values())
            for alias in project.aliases:
                if alias.id == alias_id:
                    deployed_stages = [self.stages[i] for i in range(len(project_stages)) if project_stages[i]]
                    alias_name = alias.name
                    associated_project = project.name
        
        deployed_stages = ",".join([stage.name for stage in deployed_stages]) if len(deployed_stages) > 0 else "not found" 
        return [alias_name, alias_id, deployed_stages, associated_project, associated_apis]
    
    def get_project_info(self, project_name) -> list:
        deployed_stages = []
        associated_apps = "not found"
        associated_apis = "not found"
        associated_aliases = "not found"
        
        for project in self.projects_list:
            if project_name == project.name:
                project_stages = project.get_deployed_stages()
                deployed_stages = [self.stages[i] for i in range(len(project_stages)) if project_stages[i]]
                associated_apis = [api.name_version for api in project.apis]
                associated_apps = [app.name for app in project.apps]
                associated_aliases = [alias.name for alias in project.aliases]
        deployed_stages_string = ",".join([stage.name for stage in deployed_stages]) if len(deployed_stages) > 0 else "not found" 
        associated_apis_string = ",\n".join([api_name for api_name in associated_apis]) if len(associated_apis) > 0 else "not found" 
        associated_apps_string = ",\n".join([app_name for app_name in associated_apps]) if len(associated_apps) > 0 else "not found" 
        associated_aliases_string = ",\n".join([alias_name for alias_name in associated_aliases]) if len(associated_aliases) > 0 else "not found" 
        return [project_name, deployed_stages_string, associated_apis_string, associated_apps_string, associated_aliases_string]