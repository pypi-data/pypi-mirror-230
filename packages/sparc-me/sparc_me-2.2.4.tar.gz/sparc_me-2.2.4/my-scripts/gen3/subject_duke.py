from pathlib import Path
from sparc_me.gen3.convertor import Gen3Convertor

if __name__ == '__main__':
    # Subject
    experiment = "dataset-12L_2-version-1"
    category = "subjects"
    source_dir = Path(r"C:\Users\clin864\ctt_group\sparc_datasets\dataset-12L_2-version-1")
    source = source_dir.joinpath(category + ".xlsx")
    dest_dir = Path(r"C:\Users\clin864\ctt_group\sparc_datasets\gen3\dataset-12L_2-version-1")

    data = {
        "type": "case",
        "experiments": [{"submitter_id": experiment}],
        "submitter_id": experiment + '-' + category
    }
    convertor = Gen3Convertor()
    convertor.set_schema_dir(Path(r"C:\Users\clin864\Desktop\sparc-codathon\sparc-me\my-scripts\gen3\sds_dictionary"))
    convertor.execute(source, dest_dir=dest_dir, category=category, version="2.0.0", data_template=data)
