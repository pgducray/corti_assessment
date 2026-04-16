"""
Main workflow: Audio → Transcript → Facts → SOAP Document
"""
import os
from dotenv import load_dotenv
from corti_client import CortiClient
from helpers import transcribe_audio, extract_facts, generate_soap_document


def main():
    """Execute the complete Corti API workflow"""

    # Load environment variables
    load_dotenv()

    print("=" * 70)
    print("CORTI API WORKFLOW: Audio → Transcript → Facts → SOAP")
    print("=" * 70)
    print()

    # Step 0: Initialize and authenticate
    print("Step 0: Authentication")
    print("-" * 70)
    client = CortiClient()
    client.authenticate()
    print("✓ Successfully authenticated with Corti API")
    print()

    # Step 1: Audio to Transcript
    print("Step 1: Audio → Transcript")
    print("-" * 70)
    # audio_path = "data/samples/TalkCPR- A real patient and doctor interaction filmed.mp3"
    audio_path = "data/samples/Patient Consultation with MI.mp3"

    interaction_id, transcript_id, transcript_text = transcribe_audio(client, audio_path)
    print(f"\nTranscript preview:\n{transcript_text[:200]}...\n")
    print()

    # Step 2: Transcript to Facts
    print("Step 2: Transcript → Facts")
    print("-" * 70)
    facts_result = extract_facts(client, transcript_text)
    facts_list = facts_result.get('facts', [])
    print(f"\nExtracted facts preview:")
    for i, fact in enumerate(facts_list[:5], 1):
        # Handle both string and structured fact formats
        if isinstance(fact, dict):
            fact_text = fact.get('text', str(fact))
            fact_group = fact.get('group', 'N/A')
            print(f"  {i}. [{fact_group}] {fact_text}")
        else:
            print(f"  {i}. {fact}")
    if len(facts_list) > 5:
        print(f"  ... and {len(facts_list) - 5} more")
    print()

    # Step 3: Facts to SOAP Document
    print("Step 3: Facts → SOAP Document")
    print("-" * 70)
    soap_document = generate_soap_document(client, interaction_id, facts_list)

    # Display SOAP document
    print("\n" + "=" * 70)
    print("FINAL SOAP DOCUMENT")
    print("=" * 70)

    if 'sections' in soap_document.keys():
        for chunk in soap_document['sections']:
            section = chunk.get('name')
            content = chunk.get('text', '')
            print(f"\n{section}:")
            print("-" * 70)
            print(content)
    else:
        print("No sections found in document")

    print("\n" + "=" * 70)
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Interaction ID: {interaction_id}")
    print(f"All data saved to data/ directory")


if __name__ == "__main__":
    main()
