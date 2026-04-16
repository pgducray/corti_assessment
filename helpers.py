"""
Helper functions for the Corti API workflow:
1. Audio to Transcript
2. Transcript to Facts
3. Facts to SOAP Document
"""
import os
import json
import time
import uuid
import requests
from typing import Dict, List
from corti_client import CortiClient


def transcribe_audio(client: CortiClient, audio_path: str) -> tuple[str, str, str]:
    """
    Upload audio file and get transcription

    Args:
        client: Authenticated CortiClient instance
        audio_path: Path to audio file

    Returns:
        Tuple of (interaction_id, transcript_id, transcript_text)
    """
    headers = client.get_headers(include_tenant=True)

    # Step 1: Create interaction
    print("Creating interaction...")
    interaction_payload = {
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

    response = requests.post(
        f"{client.api_url}/interactions",
        headers=headers,
        json=interaction_payload,
        timeout=30
    )
    response.raise_for_status()
    interaction_data = response.json()
    interaction_id = interaction_data["interactionId"]
    print(f"✓ Interaction created: {interaction_id}")

    # Step 2: Upload audio file
    print("Uploading audio file...")
    with open(audio_path, 'rb') as audio_file:
        files = {'file': audio_file}
        upload_headers = {
            "Authorization": f"Bearer {client.access_token}",
            "Tenant-Name": client.tenant_name
        }

        response = requests.post(
            f"{client.api_url}/interactions/{interaction_id}/recordings/",
            headers=upload_headers,
            files=files,
            timeout=60
        )
        response.raise_for_status()
        recording_data = response.json()
        recording_id = recording_data["recordingId"]
        print(f"✓ Audio uploaded: {recording_id}")

    # Step 3: Request transcription
    print("Requesting transcription...")
    transcript_payload = {
        "recordingId": recording_id,
        "primaryLanguage": "en",
        "isDictation": False,
        "isMultichannel": True,
        "diarize": True
    }

    response = requests.post(
        f"{client.api_url}/interactions/{interaction_id}/transcripts",
        headers=headers,
        json=transcript_payload,
        timeout=30
    )
    response.raise_for_status()
    transcript_data = response.json()
    transcript_id = transcript_data["id"]
    print(f"✓ Transcription requested: {transcript_id}")

    # Step 4: Wait for transcription to complete
    print("Waiting for transcription to complete...")
    transcript_result = _wait_for_transcript(client, interaction_id, transcript_id)

    # Step 5: Extract text from transcript
    transcript_text = _extract_transcript_text(transcript_result)

    # Save transcript to file
    _save_transcript(transcript_text, interaction_id)

    return interaction_id, transcript_id, transcript_text


def _wait_for_transcript(
    client: CortiClient,
    interaction_id: str,
    transcript_id: str,
    max_wait_seconds: int = 300,
    poll_interval: int = 3
) -> Dict:
    """Poll for transcript completion"""
    headers = client.get_headers(include_tenant=True)
    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        # Check status
        response = requests.get(
            f"{client.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}/status",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        status_data = response.json()
        status = status_data.get('status', 'processing')

        if status == 'completed':
            # Get full transcript
            response = requests.get(
                f"{client.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            print("✓ Transcription completed!")
            return response.json()
        elif status == 'failed':
            error_msg = status_data.get('error', 'Unknown error')
            raise Exception(f"Transcript processing failed: {error_msg}")

        time.sleep(poll_interval)

    raise TimeoutError(f"Transcript did not complete within {max_wait_seconds} seconds")


def _extract_transcript_text(transcript: Dict) -> str:
    """Extract text from transcript response"""
    transcript_parts = []

    if 'transcripts' in transcript:
        for entry in transcript['transcripts']:
            if 'text' in entry:
                transcript_parts.append(entry['text'])

    return " ".join(transcript_parts)


def _save_transcript(transcript_text: str, interaction_id: str):
    """Save transcript to file"""
    folder_name = "data/transcripts"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder_name, f"{interaction_id}_transcript.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"✓ Transcript saved to: {file_path}")


def extract_facts(client: CortiClient, text: str, output_language: str = "en-US") -> Dict:
    """
    Extract structured facts from medical text

    Args:
        client: Authenticated CortiClient instance
        text: Medical text to analyze
        output_language: Language code for output (default: "en-US")

    Returns:
        Dictionary containing facts and usage info
    """
    print("Extracting facts from text...")
    headers = client.get_headers(include_tenant=True)

    payload = {
        "context": [
            {
                "type": "text",
                "text": text
            }
        ],
        "outputLanguage": output_language
    }

    response = requests.post(
        f"{client.api_url}/tools/extract-facts",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    facts_result = response.json()

    # Save facts to file
    _save_facts(facts_result)

    print(f"✓ Extracted {len(facts_result.get('facts', []))} facts")
    return facts_result


def _save_facts(facts_result: Dict):
    """Save facts to JSON file"""
    folder_name = "data/facts"
    os.makedirs(folder_name, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(folder_name, f"facts_{timestamp}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(facts_result, f, indent=2, ensure_ascii=False)
    print(f"✓ Facts saved to: {file_path}")


def generate_soap_document(
    client: CortiClient,
    interaction_id: str,
    facts: List[Dict],
    output_language: str = "en-US"
) -> Dict:
    """
    Generate SOAP document from extracted facts

    Args:
        client: Authenticated CortiClient instance
        interaction_id: ID of the interaction
        facts: List of extracted facts (structured dictionaries with text, group, source)
        output_language: Language code for output (default: "en-US")

    Returns:
        Generated SOAP document
    """
    print("Generating SOAP document...")
    headers = client.get_headers(include_tenant=True)

    # Facts are already properly structured from extract_facts
    # Each fact should have: text, group, source
    # If facts are strings (legacy), convert them; otherwise use as-is
    formatted_facts = []
    for fact in facts:
        if isinstance(fact, str):
            # Legacy support: convert string to structured fact
            formatted_facts.append({
                "text": fact,
                "group": "others",
                "source": "core"
            })
        elif isinstance(fact, dict):
            # Use structured fact as-is (already has text, group, source)
            formatted_facts.append(fact)
        else:
            print(f"Warning: Skipping invalid fact format: {type(fact)}")

    payload = {
        "context": [
            {
                "type": "facts",
                "data": formatted_facts
            }
        ],
        "templateKey": "corti-soap",
        "outputLanguage": output_language,
        "name": "SOAP Note",
        "disableGuardrails": False,
        "documentationMode": "global_sequential"
    }

    response = requests.post(
        f"{client.api_url}/interactions/{interaction_id}/documents/",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    soap_document = response.json()

    print(f"✓ SOAP document generated!")
    print(f"Document ID: {soap_document.get('id', 'N/A')}")

    # Save SOAP document
    _save_soap_document(soap_document, interaction_id)

    return soap_document


def _wait_for_document(
    client: CortiClient,
    interaction_id: str,
    document_id: str,
    max_wait_seconds: int = 60,
    poll_interval: int = 2
) -> Dict:
    """Poll for document generation completion"""
    headers = client.get_headers(include_tenant=True)
    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        response = requests.get(
            f"{client.api_url}/interactions/{interaction_id}/documents/{document_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        document = response.json()

        status = document.get('status', 'processing')
        if status == 'completed':
            print("✓ SOAP document generated!")
            return document
        elif status == 'failed':
            raise Exception("Document generation failed")

        time.sleep(poll_interval)

    raise TimeoutError(f"Document did not complete within {max_wait_seconds} seconds")


def _save_soap_document(soap_document: Dict, interaction_id: str):
    """Save SOAP document to file"""
    folder_name = "data/soap_documents"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder_name, f"{interaction_id}_soap.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(soap_document, f, indent=2, ensure_ascii=False)
    print(f"✓ SOAP document saved to: {file_path}")
