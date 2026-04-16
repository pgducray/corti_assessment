# Corti API Assessment

Demonstration of a complete API workflow for processing medical audio into clinical documentation.

## Workflow

**Audio → Transcript → Facts → SOAP Document**

1. **Audio to Transcript**: Upload audio file, create interaction, and get transcription
2. **Transcript to Facts**: Extract structured medical facts using AI
3. **Facts to SOAP**: Generate clinical documentation in SOAP format

## Project Structure

```
.
├── corti_client.py         # Authentication & API client
├── helpers.py              # Core workflow functions
├── main.py                 # Complete workflow script
├── presentation.ipynb      # Jupyter notebook demo
├── data/
│   ├── samples/           # Audio files
│   ├── transcripts/       # Generated transcripts
│   ├── facts/             # Extracted facts
│   └── soap_documents/    # Generated SOAP docs
└── Test/                  # Original test scripts
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials in `.env`:
```
CORTI_TENANT_NAME=your_tenant
CORTI_CLIENT_ID=your_client_id
CORTI_CLIENT_SECRET=your_secret
CORTI_ENVIRONMENT=eu
```

## Usage

### Run Complete Workflow

```bash
python main.py
```

### Jupyter Notebook Presentation

```bash
jupyter notebook presentation.ipynb
```

Then convert to HTML slides:
```bash
jupyter nbconvert presentation.ipynb --to slides --post serve
```

### Use as Library

```python
from corti_client import CortiClient
from helpers import transcribe_audio, extract_facts, generate_soap_document

# Authenticate
client = CortiClient()
client.authenticate()

# Process audio
interaction_id, _, transcript = transcribe_audio(client, "audio.mp3")
facts_result = extract_facts(client, transcript)
soap_doc = generate_soap_document(client, interaction_id, facts_result['facts'])
```

## Components

### `corti_client.py`
- `CortiClient`: Handles authentication and API communication
- Methods: `authenticate()`, `get_headers()`

### `helpers.py`
- `transcribe_audio()`: Upload and transcribe audio file
- `extract_facts()`: Extract medical facts from text
- `generate_soap_document()`: Generate SOAP documentation

### `main.py`
- End-to-end workflow execution
- Console output with progress tracking

### `presentation.ipynb`
- Interactive demonstration
- Step-by-step code and outputs
- Ready for HTML slide conversion
