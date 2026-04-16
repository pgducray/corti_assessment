import requests

# Generate Document from facts

url = "https://api.{environment}.corti.app/v2/interactions/{id}/documents/"

payload = {
    "context": [
        {
            "type": "facts",
            "data": [
                {
                    "text": "<string>",
                    "group": "Others",
                    "source": "core"
                }
            ]
        }
    ],
    "templateKey": "corti-soap",
    "outputLanguage": "<string>",
    "name": "<string>",
    "disableGuardrails": True,
    "documentationMode": "global_sequential"
}
headers = {
    "Tenant-Name": "<tenant-name>",
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)

# Retrieve generated document
url = "https://api.{environment}.corti.app/v2/interactions/{id}/documents/{documentId}"

headers = {
    "Tenant-Name": "<tenant-name>",
    "Authorization": "Bearer <token>"
}

response = requests.get(url, headers=headers)

print(response.text)
