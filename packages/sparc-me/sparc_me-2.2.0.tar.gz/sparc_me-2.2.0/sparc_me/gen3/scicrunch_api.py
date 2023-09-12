import requests
import json

if __name__ == '__main__':
    dataset_id = 264
    url = "https://scicrunch.org/api/1/elastic/SPARC_PortalDatasets_pr/_search"
    api_key = "xBOrIfnZTvJQtobGo8XHRvThdMYGTxtf"
    params = {'api_key': api_key}
    body = {
        "size": 10,
        "from": 0,
        "query": {
            "match": {
                "pennsieve.identifier.aggregate": {
                    "query": str(dataset_id)
                }
            }
        },
        "_source": [
            "organisms.subject.species",
            "anatomy.organ"
        ]
    }

    headers = {
        'Content-Type': 'text/plain',
    }

    response = requests.request("POST", url, headers=headers, json=body, params=params)
    result = response.json()

    print(json.dumps(result, indent=4))

    # get organs
    organ_list = list()
    hits = result.get("hits").get("hits")
    for hit in hits:
        try:
            organs = hit.get("_source").get("anatomy").get("organ")
        except AttributeError:
            continue
        for organ in organs:
            organ = organ.get("name")
            if organ:
                organ_list.append(organ)
    # remove duplicates
    organs = [*set(organ_list)]
    print("Organs:")
    print(organ_list)

    # get species
    species_list = list()
    for hit in hits:
        try:
            subjects = hit.get("_source").get("organisms").get("subject")
        except AttributeError:
            continue
        for subject in subjects:
            try:
                species = subject.get("species").get("name")
            except AttributeError:
                continue
            if species:
                species_list.append(species)
    species_list = [*set(species_list)]
    print("Species")
    print(species_list)
