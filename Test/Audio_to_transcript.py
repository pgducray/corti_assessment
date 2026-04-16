import requests
import os
import uuid
import time


# Authenticate user and get access token

## Initialize the CortiClient by pulling credentials from the environment.
tenant_name = os.getenv("CORTI_TENANT_NAME")
client_id = os.getenv("CORTI_CLIENT_ID")
client_secret = os.getenv("CORTI_CLIENT_SECRET")
environment = os.getenv("CORTI_ENVIRONMENT", "eu")

## Auth URL - Corti uses Keycloak with realm pattern
auth_url = f"https://auth.{environment}.corti.app/realms/{tenant_name}/protocol/openid-connect/token"

## Check if credentials are present
if bool(self.tenant_name and self.client_id and self.client_secret):
    print("Credentials missing. Check your .env file.")

## Prepare payload for authentication request
payload = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "openid"
}

## Make authentication request and handle potential errors
last_error = None
try:
    response = requests.post(self.auth_url, data=payload, timeout=10)
    response.raise_for_status()
    access_token = response.json().get("access_token")

except requests.exceptions.RequestException as e:
    last_error = e
print(last_error)

# Create Interaction

api_url = f"https://api.{environment}.corti.app/v2/interactions/"

payload = {
    "encounter": {
        "identifier": str(uuid.uuid4()),
        "status": "planned",
        "type": "first_consultation"
    },
    "patient": {
        "identifier": str(uuid.uuid4()),
        "gender": "unknown"
    }
}
headers = {
    "Tenant-Name": tenant_name,
    "Authorization":f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{self.api_url}/interactions",
    headers=headers,
    json=payload,
    timeout=30
)
response.raise_for_status()
print(response.json())

# Upload audio file for trasncription
url = "https://api.{environment}.corti.app/v2/interactions/{id}/recordings/"

payload = "<string>"

response = requests.post(url, json=payload, headers=headers)

print(response.text)

# Create transcription request
url = "https://api.{environment}.corti.app/v2/interactions/{id}/transcripts/"

payload = {
    "recordingId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "primaryLanguage": "en",
    "isDictation": True,
    "isMultichannel": True,
    "diarize": True,
    "participants": [
        {
            "channel": 123,
            "role": "doctor"
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)

# wait for transcription to complete and retrieve result

## Check Status

def get_transcript_status(self, interaction_id: str, transcript_id: str) -> Dict:
        """
        Check the status of a transcript (processing/completed/failed).

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript

        Returns:
            Status object with status field
        """
        headers = self.get_headers(include_tenant=True)
        response = requests.get(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}/status",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()



## Wait for completion according to status and get transcript result
def wait_for_transcript(
        self,
        interaction_id: str,
        transcript_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 2
    ) -> Dict:
        """
        Poll for transcript completion with timeout.

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript
            max_wait_seconds: Maximum time to wait in seconds (default: 5 minutes)
            poll_interval: Seconds between status checks (default: 2)

        Returns:
            Final transcript when completed

        Raises:
            TimeoutError: If transcript doesn't complete within max_wait_seconds
            Exception: If transcript processing fails
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            status_response = get_transcript_status(interaction_id, transcript_id)
            status = status_response.get('status', 'processing')

            if status == 'completed':
                response = requests.get(
                    f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            elif status == 'failed':
                error_msg = status_response.get('error', 'Unknown error')
                raise Exception(f"Transcript processing failed: {error_msg}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Transcript did not complete within {max_wait_seconds} seconds")

# Save transcription result to file

transcript_parts = []

if 'transcripts' in transcript:
    for entry in transcript['transcripts']:
        # Check if the key exists and matches the channel
        if entry.get('channel') == 1 and 'text' in entry:
            transcript_parts.append(entry['text'])

## Join the list into a single string separated by a space (or newline)
transcript_text = " ".join(transcript_parts)

folder_name = "transcripts_text"

## Create folder if it doesn't exist
os.makedirs(folder_name, exist_ok=True)

## Properly join folder and file name
file_path = os.path.join(folder_name, file_name)

## Write the transcript_text to the file
try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"✅ Transcript successfully saved to: {file_path}")
except Exception as e:
    print(f"❌ An error occurred while saving transcript: {e}")



print(response.text)
