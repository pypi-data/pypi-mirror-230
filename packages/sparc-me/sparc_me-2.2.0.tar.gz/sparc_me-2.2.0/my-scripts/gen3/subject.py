from pathlib import Path
from sparc_me.gen3.convertor import Gen3Convertor

if __name__ == '__main__':
    # subject
    experiment = "dataset-264-version-1"
    category = "subjects"
    source_dir = Path(r"C:\Users\clin864\ctt_group\sparc_datasets")
    source_dir = source_dir.joinpath(experiment)
    source = source_dir.joinpath(category + ".xlsx")
    dest_dir = source_dir

    data = {
        "type": "case",
        "experiments": [{"submitter_id": experiment}],
        "submitter_id": experiment + '-' + category
    }
    convertor = Gen3Convertor()
    convertor.set_schema_dir(Path(r"C:\Users\clin864\Desktop\sparc-codathon\sparc-me\my-scripts\gen3\sds_dictionary"))
    convertor.execute(source, dest_dir=dest_dir, category=category, version="1.2.3", data_template=data)
