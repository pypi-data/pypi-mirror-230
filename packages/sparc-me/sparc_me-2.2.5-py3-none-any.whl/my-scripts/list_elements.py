from sparc_me import Dataset

if __name__ == "__main__":
    dataset = Dataset()

    # List elements/fields
    elements = dataset.list_elements(category="dataset_description", version="1.2.3")
    # elements = dataset.list_elements(category="subjects", version="2.0.0")
    print(elements)
