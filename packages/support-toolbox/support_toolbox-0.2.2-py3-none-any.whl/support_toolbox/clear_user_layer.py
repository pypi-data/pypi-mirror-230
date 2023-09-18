import json
import requests

# Resource Types currently supported
entities = {
    'ANALYSIS': 'https://dwec.data.world/v0/Analysis',
    'BUSINESS_TERM': 'https://dwec.data.world/v0/BusinessTerm',
    'COLLECTION': 'https://dwec.data.world/v0/Catalog',
    'COLUMN': 'https://dwec.data.world/v0/DatabaseColumn',
    'DATA_TYPE': 'http://www.w3.org/ns/csvw#Datatype',
    'DATASET': 'https://dwec.data.world/v0/DwDataset',
    'TABLE': 'https://dwec.data.world/v0/DatabaseTable'
}


# Clear User/Edit Layer on entire resource
def clear_user_layer(api_token, org, iri, resource_type):
    clear_user_layer_url = f"https://api.data.world/v0/metadata/{org}/resources/clear"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    clear_resource_data = {
        "resources": [iri],
        "resourceType": resource_type
    }

    body = json.dumps(clear_resource_data)
    response = requests.post(clear_user_layer_url, body, headers=header)

    # Verify the deletion
    if response.status_code == 200:
        print(f"Successfully cleared the User Layer for: {iri}")
    else:
        print(response.text)


def run():
    api_token = input("Enter your API Token for the site you are looking to clear the user layer of a resource on: ")
    org = input("Enter the org_id the resource is in: ")
    iri = input("Enter the resource iri: ")

    while True:
        for i, entity in enumerate(entities, start=1):
            print(f"{i}. {entity}")

        try:
            selection = int(input("Enter the number corresponding with the parent type of the resource you need to clear: "))
            if 1 <= selection <= len(entities):
                resource_type = list(entities.values())[selection - 1]
                clear_user_layer(api_token, org, iri, resource_type)
                break  # Exit the loop if a valid selection is made
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
