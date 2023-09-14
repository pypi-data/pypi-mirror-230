import json
import requests
import ast


def get_api_token(cred_file, url):
    with open(cred_file) as f:
        credentials = json.load(f)
    key = {
        "api_key": credentials.get("api_key"),
        "key_id": credentials.get("key_id")
    }
    token = requests.post(url + "/user/credentials/cdis/access_token", json=key).json()

    return token


def query_data(endpoint, headers, query):
    url = endpoint + "/api/v0/submission/graphql/"

    ql = requests.post(url, json=query, headers=headers)
    data = ast.literal_eval(str(ql.text))
    return data


if __name__ == '__main__':
    experiment_submitter_ids = ["dataset-141-version-3"]
    cred_file = r"C:\Users\clin864\Desktop\sparc-codathon\sparc-me\sparc_me\gen3\credentials.json"
    endpoint = "http://gen3.abi-ctt-ctp.cloud.edu.au"

    query = {"query": """{
            project(project_id: "demo1-12L"){
                id,
                project_id,
                experiments(first: 1000){
                    id,
                    submitter_id,
                    dataset_descriptions(first: 1000){
                        id,
                        submitter_id
                    },
                    cases(first: 1000){
                        id,
                        submitter_id
                    },
                    manifests(first: 1000){
                        id,
                        submitter_id
                    }
                }
            }
        }"""}

    token = get_api_token(cred_file=cred_file, url=endpoint)
    headers = {'Authorization': 'bearer ' + token['access_token']}

    data = query_data(endpoint, headers, query)
    print(data)

    projects = data.get("data").get("project")

    experiment_uids = list()
    dataset_description_uids = list()
    case_uids = list()
    manifest_uids = list()
    for project in projects:
        experiments = project.get("experiments")
        for experiment in experiments:
            experiment_submitter_id = experiment.get("submitter_id")
            if experiment_submitter_id not in experiment_submitter_ids:
                continue
            experiment_uid = experiment.get("id")
            experiment_uids.append(experiment_uid)

            dataset_descriptions = experiment.get("dataset_descriptions")
            for dataset_description in dataset_descriptions:
                dataset_description_uid = dataset_description.get("id")
                dataset_description_uids.append(dataset_description_uid)

            cases = experiment.get("cases")
            for case in cases:
                case_uid = case.get("id")
                case_uids.append(case_uid)

            manifests = experiment.get("manifests")
            for manifest in manifests:
                manifest_uid = manifest.get("id")
                manifest_uids.append(manifest_uid)

    print("experiment_uids UIDs: " + str(experiment_uids))
    print("dataset_description UIDs: " + str(dataset_description_uids))
    print("case(subject) UIDs: " + str(case_uids))
    print("manifest UIDs: " + str(manifest_uids))

    uids = manifest_uids + case_uids + dataset_description_uids + experiment_uids
    print("UIDs: " + str(uids))
