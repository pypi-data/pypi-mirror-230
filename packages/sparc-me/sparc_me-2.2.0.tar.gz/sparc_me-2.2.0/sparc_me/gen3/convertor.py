import os
from pathlib import Path
import pandas as pd
from xlrd import XLRDError
import json
import yaml
import re


class Gen3Convertor(object):
    def __init__(self):
        self._category = None
        self._supported_versions = ["1.2.3", "2.0.0"]
        self._current_dir = Path(__file__).parent.resolve()
        self._resources_dir = self._current_dir.parent / "resources"
        self._templates_dir = self._resources_dir / "templates"
        self._schema_dir = None
        self._special_chars = ['/', '_']

        self._row_based = ["manifest", "subjects", "samples"]
        self._col_based = ["dataset_description"]

    def set_schema_dir(self, path):
        self._schema_dir = Path(path)

    def set_category(self, category):
        self._category = category

    def execute(self, source, dest_dir, category, version, data_template=dict()):
        self._validate_version(version)

        self._category = category
        mappings = self._get_mappings(version)

        data = None
        if category in self._row_based:
            if category == "manifest":
                sources = self._get_files(source, category)
            else:
                sources = [source]

            metadata_pd_composite = None
            for source in sources:
                metadata_pd = self._get_sparc_metadata(source)
                metadata_pd = self._map_fields(metadata_pd, mappings, target_version="2.0.0")

                if metadata_pd_composite is not None:
                    metadata_pd_composite = pd.concat([metadata_pd_composite, metadata_pd], ignore_index=True)
                else:
                    metadata_pd_composite = metadata_pd

            metadata_list_dict = metadata_pd_composite.to_dict('records')

            schema = self._get_schema(self._category)
            properties = schema.get("properties")
            system_properties = schema.get("systemProperties")
            required = schema.get("required")

            data_list = list()
            for metadata_dict in metadata_list_dict:
                data = data_template.copy()
                for property in properties.items():
                    key = property[0]

                    if key in system_properties:
                        continue
                    if data.get(key):
                        continue

                    value = metadata_dict.get(key)

                    # Update submitter_id
                    if key in ["subject_id", "filename"]:
                        data["submitter_id"] = data["submitter_id"] + '-' + value
                        data["submitter_id"] = data["submitter_id"].replace('./', '')
                        data["submitter_id"] = re.sub(str(self._special_chars), '-', data["submitter_id"])

                    # check if value exists and if value equals to nan (nan variable does not equal to itself)
                    if value and value == value:
                        if len(value) == 1:
                            value = value[0]

                        # handle special values
                        if isinstance(value, str):
                            value = value.replace("\"", "\'")

                            # separate string by new line "\n" and saved in a list if the list > 1
                            value_list = value.split("\n")
                            if len(value_list) > 1:
                                value = value_list

                        data[key] = value
                    else:
                        if key in required:
                            data[key] = "NA"

                data_list.append(data)
                del data
            data = data_list
        elif category in self._col_based:
            metadata_pd = self._get_sparc_metadata(source)
            metadata_pd = self._map_fields(metadata_pd, mappings, target_version="2.0.0")
            data = self._convert(metadata_pd, data_template)

        if dest_dir:
            filename = category + ".json"
            dest = dest_dir.joinpath(filename)
            self._save(data, dest)

        return data

    def _get_files(self, source, category):
        files = list()
        if source.is_file():
            files.append(source)
        elif source.is_dir():
            filename = category + ".xlsx"
            for file in source.rglob(filename):
                files.append(file)
        else:
            raise FileNotFoundError("File not found")
        return files

    def _validate_version(self, version):
        if version not in self._supported_versions:
            raise Exception("Dataset version not supported")

    @staticmethod
    def read_excel(path, sheet_name=None):
        try:
            # the read_excel method return dict when sheet name is passed. otherwise a dataframe will be returned
            if sheet_name:
                metadata = pd.read_excel(path, sheet_name=sheet_name)
            else:
                metadata = pd.read_excel(path)
        except XLRDError:
            if sheet_name:
                metadata = pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')
            else:
                metadata = pd.read_excel(path, engine='openpyxl')

        return metadata

    def _get_mappings(self, version):
        version = version.replace(".", "_")
        version = "version_" + version
        version_dir = self._templates_dir / version
        mapping_file = version_dir / "element_mapping_gen3.xlsx"

        mappings = self.read_excel(mapping_file, self._category)

        return mappings

    def _save(self, data, dest):
        os.makedirs(dest.parent, exist_ok=True)
        with open(dest, 'w') as f:
            json.dump(data, f, indent=4)
        print("Saved to " + str(dest))

    def _get_schema(self, category):
        if category == "subjects":
            category = "case"
        if category == "samples":
            category = "sample"
        schema_file = category + ".yaml"
        schema_file = self._schema_dir / schema_file
        with open(schema_file, 'r') as stream:
            schema = yaml.safe_load(stream)

            # encoding = "utf8"

        return schema

    def _get_sparc_metadata(self, source):
        metadata_sparc = self.read_excel(source)
        if source.stem == "dataset_description":
            # combine values
            metadata_sparc["values"] = metadata_sparc.iloc[:, 3:].values.tolist()
            metadata_sparc["values"] = metadata_sparc["values"].apply(lambda x: [i for i in x if str(i) != "nan"])

            # Extract columns
            # Element name: 1st column
            # Values: last column
            metadata_sparc = metadata_sparc[[metadata_sparc.columns[0], metadata_sparc.columns[-1]]]

        return metadata_sparc

    def _map_fields(self, metadata_sparc, mappings, target_version):
        if self._category == "dataset_description":
            nums_of_records = len(metadata_sparc)
            column_idx = 0
            elements = metadata_sparc.iloc[:, column_idx].tolist()

            for idx in range(nums_of_records):
                element = elements[idx]
                try:
                    record = mappings[mappings['element'] == element]
                    metadata_sparc.loc[idx, metadata_sparc.columns[0]] = record.iloc[0]["gen3_element_" + target_version]
                except:
                    continue

            metadata_sparc = metadata_sparc.dropna()
        else:
            column_headers = list(metadata_sparc.columns)
            for idx, column_header in enumerate(column_headers):
                record = mappings[mappings['element'].str.lower() == column_header.lower()]
                if record.empty:
                    continue
                new_name = record.iloc[0]["gen3_element_" + target_version]

                metadata_sparc = metadata_sparc.rename(columns={column_header: new_name})

            metadata_sparc = metadata_sparc.loc[:, metadata_sparc.columns.notna()]

        return metadata_sparc

    def _convert(self, metadata_pd, data):
        metadata_dict = dict()
        records = metadata_pd.to_dict(orient='records')

        if self._category == "dataset_description":
            for record in records:
                element = record.get("Metadata element")
                values = record.get("values")
                metadata_dict[element] = values

        schema = self._get_schema(self._category)
        properties = schema.get("properties")
        system_properties = schema.get("systemProperties")
        required = schema.get("required")

        for property in properties.items():
            key = property[0]

            if key in system_properties:
                continue
            if data.get(key):
                continue

            value = metadata_dict.get(key)

            if value:
                if self._category in self._row_based and len(value) == 1:
                    value = value[0]

                data[key] = value
            else:
                if key in required:
                    if self._category in self._col_based:
                        data[key] = []
                    else:
                        data[key] = "NA"
        return data
