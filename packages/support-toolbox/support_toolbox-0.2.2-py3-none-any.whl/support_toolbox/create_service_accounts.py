import requests
import json

owner = "datadotworldsupport"
SERVICE_ACCOUNTS = [
    {
        "desiredUsername": "ctk",
        "displayName": "DDW Catalog Toolkit Service"
    },
    {
        "desiredUsername": "ddwmetrics",
        "displayName": "DDW Platform Metrics Service"
    }
]


def create_service_account(api_token, payload):
    create_service_account_url = f"https://api.data.world/v0/serviceaccount/{owner}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    body = json.dumps(payload)

    # Create the service account
    response = requests.post(create_service_account_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        response_json = response.json()
        print(f"username: {response_json['serviceAccountUsername']}\ntoken: {response_json['token']}")
    else:
        print(response.text)


def run():
    api_token = input("Enter your API Token for the site you are deploying service accounts to: ")
    for sa in SERVICE_ACCOUNTS:
        create_service_account(api_token, sa)
