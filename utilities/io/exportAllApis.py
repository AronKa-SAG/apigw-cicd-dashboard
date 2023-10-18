from requests.auth import HTTPBasicAuth
import json, sys, time, requests, urllib3

#Init Variables from arguments
host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
passw = sys.argv[4]
azure_token = sys.argv[5]

def call_apiexport_pipeline(apiId, apiName, azure_token):
    print("     Call Export Api Project with params: apiid:{}, apiProject:{}".format(apiId, apiName))
    headers = {'Content-Type': 'application/json','Accept': 'application/json'}
    url = "https://dev.azure.com/schwarzit/schwarzit.esb/_apis/pipelines/13553/runs?api-version=6.0-preview.1"
    payload = json.dumps({
                "stagesToSkip": [],
                "resources": {
                    "repositories": {
                        "self": {
                            "refName": "refs/heads/master"
                        }
                    }
                },
                "variables": {
                    "apiId": {
                        "value": str(apiId),
                        "isSecret": False
                    },
                    "apiProject": {
                        "value": str(apiName),
                        "isSecret": False
                    }
                    ,
                    "exportFrom": {
                        "value": "DEV",
                        "isSecret": False
                    }
                }
            })

    print(payload)
    response_export = requests.request("POST", url=url, headers=headers,auth = HTTPBasicAuth('', azure_token), data=payload, verify=False)
    print("Export pipeline call reponse code: {}".format(response_export.status_code))
   
    if response_export.status_code >= 200 and response_export.status_code < 300:
        print("OK")
    else:
         print("Export pipeline call failed reponse text: {}".format(response_export.json))

def get_apis_and_export(host, port, user, passw, azure_token):
    print("Export apis from host: {}:{}".format(host, port))
    headers = {'Content-Type': 'application/json','Accept': 'application/json'}
    url = "https://{}:{}/rest/apigateway/apis".format(host, port)
    auth = HTTPBasicAuth(user, passw)
    responseGet = requests.request("GET", url=url, auth=auth, headers=headers, verify=False)
    if responseGet.status_code == 200:
        jsonResponseGet = responseGet.json()
        if len(jsonResponseGet["apiResponse"]) > 0:
            for api in jsonResponseGet["apiResponse"]:
                #print("Export Api with Name:{} and ID:{}".format(api["api"]["apiName"],api["api"]["id"]))
                print("########################################################")
                call_apiexport_pipeline(api["api"]["id"], api["api"]["apiName"], azure_token)
                time.sleep(70)
        else:
            print(jsonResponseGet)
    else:
        print(responseGet)

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore
    get_apis_and_export(host, port, user, passw, azure_token)

if __name__ == '__main__':
    main()