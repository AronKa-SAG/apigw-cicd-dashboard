from flask import Flask, render_template
from dashboard.apigwData import ApigwData

new_data = ApigwData()
app = Flask(__name__)

@app.route('/')
def home():
    project_list = new_data.get_projects_per_stage()
    header_list = ["Project"] + new_data.stages
    return render_template('index.html', header_list=header_list, project_list=project_list)

@app.route("/apis")
def apis():
    # print(f"new data: {new_data.projects_list}", file=sys.stdout)
    api_list = new_data.get_apis_per_stage()
    header_list = ["API"] + new_data.stages
    # print(f"assets on stages: {new_data.assets_on_stages}", file=sys.stdout)
    return render_template("apis.html", header_list=header_list, api_list=api_list)

@app.route("/applications")
def applications():
    app_list = new_data.get_apps_per_stage()
    header_list = ["Application"] + new_data.stages
    #print(f"apps on stages: {app_list}", file=sys.stdout)
    return render_template("applications.html", header_list=header_list, application_list=app_list)

@app.route("/aliases")
def aliases():
    alias_list = new_data.get_aliases_per_stage()
    header_list = ["Alias"] + new_data.stages
    return render_template("aliases.html", header_list=header_list, alias_list=alias_list)

@app.route('/refresh', methods=['GET'])
def refresh_data():
    new_data.refresh_all_stages()
    return "Data successfully loaded from all API Gateway stages!"

@app.route('/modal/api/<api_id>')
def api_modal(api_id):
    api_modal_structure = new_data.get_api_info(api_id)
    return render_template("modal_api.html", api_modal=api_modal_structure)

@app.route('/modal/app/<app_id>')
def app_modal(app_id):
    app_modal_structure = new_data.get_app_info(app_id)
    return render_template("modal_app.html", app_modal=app_modal_structure)

@app.route('/modal/alias/<alias_id>')
def alias_modal(alias_id):
    alias_modal_structure = new_data.get_alias_info(alias_id)
    return render_template("modal_alias.html", alias_modal=alias_modal_structure)

@app.route('/modal/project/<project_name>')
def project_modal(project_name):
    project_modal_structure = new_data.get_project_info(project_name)
    return render_template("modal_project.html", project_modal=project_modal_structure)

