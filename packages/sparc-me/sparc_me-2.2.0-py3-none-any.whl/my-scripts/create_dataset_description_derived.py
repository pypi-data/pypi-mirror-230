"""
Example for generating a SDS derived dataset dataset and filling the dataset_description
"""

from sparc_me import Dataset
from sparc_me.core.utils import add_data

if __name__ == '__main__':
    # dataset_path = "./tmp/example/derived_dataset/"
    # file_path = "./tmp/example/derived_dataset/tmp.txt"

    dataset_path = "C:\\Users\\clin864\\ctt_group\\sparc_datasets\\dataset-12L_1-version-1 - Copy"
    file_path = "C:\\Users\\clin864\\ctt_group\\sparc_datasets\\tmp.txt"

    dataset = Dataset()

    # Creating a SDS dataset
    dataset.load_from_template(version="2.0.0")
    dataset.save(save_dir=dataset_path)

    # load dataset
    # dataset1 = dataset.load_dataset(dataset_path)

    # Filling/Updating dataset.

    # Filling dataset description
    # the values can be filled in by 2 methods, set_field() or set_field_using_row_name().
    # Using Dataset.set_field()
    # You can get the row_index by looking at
    #   1. the saved metadata file dataset_description.xlsx. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2.
    #   2. or the DataFrame object in the python code. dataset._dataset.dataset_description.metadata
    #
    dataset.set_field(category="dataset_description", row_index=2, header="Value", value="2.0.0")
    dataset.set_field(category="dataset_description", row_index=3, header="Value", value="experimental")
    dataset.set_field(category="dataset_description", row_index=5, header="Value", value="Duke Breast Cancer MRI segmentation")
    dataset.set_field(category="dataset_description", row_index=6, header="Value", value="NA")
    dataset.set_field(category="dataset_description", row_index=7, header="Value", value="Breast cancer")
    dataset.set_field(category="dataset_description", row_index=11, header="Value", value="Segmenting breast MRI")
    dataset.set_field(category="dataset_description", row_index=12, header="Value", value="derived from Duke Breast Cancer MRI dataset")
    dataset.set_field(category="dataset_description", row_index=13, header="Value", value="NA")
    dataset.set_field(category="dataset_description", row_index=14, header="Value", value="breast")
    dataset.set_field(category="dataset_description", row_index=15, header="Value", value="Machine-learning")
    dataset.set_field(category="dataset_description", row_index=16, header="Value", value="Tensorflow 1")
    dataset.set_field(category="dataset_description", row_index=17, header="Value", value="NA")
    dataset.set_field(category="dataset_description", row_index=19, header="Value", value="Lin, Chinchien")
    dataset.set_field(category="dataset_description", row_index=20, header="Value", value="https://orcid.org/0000-0001-8170-199X")
    dataset.set_field(category="dataset_description", row_index=21, header="Value", value="University of Auckland")
    dataset.set_field(category="dataset_description", row_index=22, header="Value", value="Researcher")
    dataset.set_field(category="dataset_description", row_index=24, header="Value", value="source")
    dataset.set_field(category="dataset_description", row_index=25, header="Value", value="WasDerivedFrom")
    dataset.set_field(category="dataset_description", row_index=26, header="Value", value="https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=70226903")
    dataset.set_field(category="dataset_description", row_index=27, header="Value", value="URL")
    dataset.set_field(category="dataset_description", row_index=29, header="Value", value="923")
    dataset.set_field(category="dataset_description", row_index=30, header="Value", value="5032")

    # Saving the updated dataset
    dataset.save(dataset_path)

    # adding data
    add_data(file_path, dataset_path, copy=True, overwrite=False)
