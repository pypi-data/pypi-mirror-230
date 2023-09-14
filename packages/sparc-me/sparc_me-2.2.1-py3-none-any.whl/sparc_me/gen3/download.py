from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

def main():
    endpoint = "http://gen3.abi-ctt-ctp.cloud.edu.au"
    cred_file = "credentials.json"

    auth = Gen3Auth(refresh_file=cred_file)

    sub = Gen3Submission(endpoint, auth)
    program = "demo1"
    project = "12L"
    node_type = "dataset_description"
    fileformat = "json"
    filename = r"C:\Users\clin864\ctt_group\sparc_datasets\dataset_description_all_tmp.json"
    # sub.export_node(program, project, node_type, fileformat, filename)
    sub.export_node(program, project, node_type, fileformat)


if __name__ == "__main__":
    main()
