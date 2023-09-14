from pathlib import Path
from sparc_me.core.utils import convert_schema_excel_to_json


if __name__ == "__main__":
    source_path = Path(
        r"C:\Users\clin864\OneDrive - The University of Auckland\Desktop\sparc-codathon\sparc-me\sparc_me\resources\templates\version_2_0_0\schema.xlsx")
    dest_path = Path(
        r"C:\Users\clin864\OneDrive - The University of Auckland\Desktop\sparc-codathon\sparc-me\sparc_me\resources\templates\version_2_0_0\schema.json")

    convert_schema_excel_to_json(source_path=source_path, dest_path=dest_path)


