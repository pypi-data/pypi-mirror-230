from pathlib import Path
import json
import os

if __name__ == '__main__':
    dest = Path(r"C:\Users\clin864\ctt_group\sparc_datasets\gen3\dataset-12L_7-version-1")
    data = {
        "type": "experiment",
        "submitter_id": "dataset-12L_7-version-1",
        "projects": [
            {
                "code": "12L"
            }
        ],
        # "experimental_description": "MRI BREAST BILATERAL WWO",
        # "data_description": "https://doi.org/10.7937/TCIA.e3svre93"
    }

    # saving
    os.makedirs(dest, exist_ok=True)

    dest = dest.joinpath("experiment.json")
    with open(dest, 'w') as f:
        json.dump(data, f, indent=4)
    print("Saved to " + str(dest))
