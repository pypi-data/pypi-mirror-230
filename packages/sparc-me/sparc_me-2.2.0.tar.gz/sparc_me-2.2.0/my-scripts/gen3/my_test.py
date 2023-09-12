from pathlib import Path
import yaml
if __name__ == '__main__':
    path = Path(r"C:\Users\clin864\Desktop\sparc-codathon\sparc-me\my-scripts\gen3\sds_dictionary\case.yaml")
    with open(path, 'r') as stream:
        schema = yaml.safe_load(stream)

    pass
