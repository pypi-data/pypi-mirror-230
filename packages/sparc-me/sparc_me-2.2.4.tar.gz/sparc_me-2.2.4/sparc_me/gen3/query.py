import json
import requests

# import gen3
from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission


def graphql_api():
    # project_id = "demo1-12L"
    #
    # token = get_api_token(cred_file=cred_file, url=BASE_URL)
    # headers = {'Authorization': 'bearer ' + token['access_token']}
    # print("Headers:" + str(headers))
    #
    # # get projects
    # query = {'query': """{project(first:0){project_id id}}"""}
    # url = BASE_URL + "/api/v0/submission/graphql/"
    #
    # ql = requests.post(url, json=query, headers=headers)
    # print(ql.text)
    #
    # print("done")

    # "http://gen3.abi-ctt-ctp.cloud.edu.au/data/download/ca59f43f-362b-4179-b71e-963a7dcc22ba"
    pass


def get_api_token(cred_file, url):
    with open(cred_file) as f:
        credentials = json.load(f)
    key = {
        "api_key": credentials.get("api_key"),
        "key_id": credentials.get("key_id")
    }
    token = requests.post(url + "/user/credentials/cdis/access_token", json=key).json()

    return token


def init_submisstor(cred_file, base_url):
    auth = Gen3Auth(base_url, refresh_file=cred_file)
    sub = Gen3Submission(auth)

    return sub


def query_graphql(sub, query_string, variables=None):
    responses = sub.query(query_string, variables).get("data")

    return responses


def get_experiemnts(sub, experiments=None):
    pass

def get_subjects(sub, experiments=None, subjects=None):
    pass

def get_samples(sub, experiments=None, subjects=None, samples=None):
    pass

def get_programs(sub):
    response = sub.get_programs()

    programs = list()
    for resp in response.get("links"):
        program = resp.split('/')[-1]
        programs.append(program)

    return programs


def get_projects(sub, program):
    response = sub.get_projects(program)

    projects = list()
    for resp in response.get("links"):
        project = resp.split('/')[-1]
        projects.append(project)

    return projects


def get_node_records(sub, node, program, project):
    resp = sub.export_node(program, project, node, "json")
    records = resp.get("data")
    return records


if __name__ == '__main__':
    cred_file = "credentials.json"
    BASE_URL = "https://gen3.abi-ctt-ctp.cloud.edu.au"

    sub = init_submisstor(cred_file, BASE_URL)

    programs = get_programs(sub)
    print("Programs: " + str(programs))
    projects = get_projects(sub, programs[0])
    print(str(programs[0]) + ": " + str(projects))

    experiments = get_node_records(sub, "experiment", programs[0], projects[0])
    print(experiments)

    subjects = get_node_records(sub, "case", programs[0], projects[0])
    print(subjects)

    print("GraphQL")
    query_string = """
        { project(first:0) { code } }
    """
    query_string = """
        { project{ name } }
    """
    query_string = """
        { experiment{ submitter_id }}
    """
    query_string = """
        { 
            experiment (submitter_id: "dataset_duke"){
                submitter_id
            }
        }
    """
    query_string = """
        {
          experiment(submitter_id: "1.3.6.1.4.1.14519.5.2.1.186051521067863971269584893740842397538"){
            id
            submitter_id
            cases{
              id
              submitter_id,
              subject_id,
              samples{
                id
                submitter_id,
                sample_id
              }
            }
          }
        }
    """

    query_string = """
            {
              experiment(submitter_id: "1.3.6.1.4.1.14519.5.2.1.186051521067863971269584893740842397538"){
                id,
                submitter_id
                manifests{
                  id,
                  submitter_id
                }
              }
            }
        """
    results = query_graphql(sub, query_string)
    print(results)
