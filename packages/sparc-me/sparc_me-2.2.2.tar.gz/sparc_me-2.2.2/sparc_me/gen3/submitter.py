import json
from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

def main():
    endpoint = "http://gen3.abi-ctt-ctp.cloud.edu.au"
    cred_file = "credentials.json"
    filename = r"C:\Users\clin864\ctt_group\sparc_datasets\dataset-46-version-2\manifest_tmp.json"
    with open(filename) as f:
        data = json.load(f)


    auth = Gen3Auth(refresh_file=cred_file)

    sub = Gen3Submission(endpoint, auth)
    sub.submit_record("demo1", "12L", json=data)


if __name__ == "__main__":
    main()
