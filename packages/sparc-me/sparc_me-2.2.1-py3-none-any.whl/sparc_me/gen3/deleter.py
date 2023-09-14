from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission


def main():
    endpoint = "http://gen3.abi-ctt-ctp.cloud.edu.au"
    cred_file = "credentials.json"
    uuids = ['cb03070e-63ae-44f8-a1ba-ca2291cc3af2', "cdd5535b-d542-4e6b-8cdc-442e29e75797", "1613a9bf-6d2b-4a2c-9cdf-f205328302ba"]
    # uuids = ['b7c00f05-0cf7-448b-bf7e-56974e5994e5', '0465c3ef-8114-433a-b2af-f952e2e1e84e',
    #          '47386ce1-9030-4c24-85e2-81cd867a200c', 'f6370608-4007-4639-8635-2e2638f77f36',
    #          'e0ad2bf2-e1c4-49ce-a894-12f8b8889993', '6237f315-6180-4abf-8c03-8d7d0dd17e75',
    #          '68ad8534-07d3-47b1-9989-8f73aa580734', 'b91569f4-e9fa-41d4-a9ef-f5b0d8fac1a8',
    #          'f1198c3b-54fd-411e-9620-282f4b2d0850', '3482e631-9ebe-4c7d-a359-96160acb28b9']

    auth = Gen3Auth(refresh_file=cred_file)

    sub = Gen3Submission(endpoint, auth)

    sub.delete_records("demo1", "12L", uuids=uuids)


if __name__ == "__main__":
    main()
