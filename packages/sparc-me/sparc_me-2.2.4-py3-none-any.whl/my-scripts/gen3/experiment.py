from pathlib import Path
import json
import os

if __name__ == '__main__':
    experiment = "dataset-264-version-1"
    dest = Path(r"C:\Users\clin864\ctt_group\sparc_datasets")
    dest = dest.joinpath(dest, experiment)
    data = {
        "type": "experiment",
        "submitter_id": experiment,
        "projects": [
            {
                "code": "12L"
            }
        ]
    }

    # saving
    os.makedirs(dest, exist_ok=True)

    dest = dest.joinpath("experiment.json")
    with open(dest, 'w') as f:
        json.dump(data, f, indent=4)
    print("Saved to " + str(dest))
