# User Manual

## Overview

RAG Chatbot is a local Streamlit application for asking questions about uploaded PDF,
TXT, and Markdown documents. It builds a small retrieval index from the uploaded
files, finds relevant passages for each question, and returns grounded answers with
source references.

## Requirements

- Python 3.11 or later
- A terminal or command prompt
- Documents with selectable text

## Installation

Install the application dependencies:

```bash
pip install -r requirements.txt
```

For development and quality checks, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

## Using the Chatbot

1. Upload one or more supported documents from the sidebar.
2. Click **Build / Refresh Index** to process the files.
3. Enter a question in the chat input.
4. Review the generated answer and the cited source passages.

## Troubleshooting

- If the app says no documents are indexed, upload files and rebuild the index.
- If answers are incomplete, add more relevant source documents.
- If a scanned PDF returns little or no text, run OCR on the PDF first.
- If dependencies are missing, reinstall from `requirements.txt`.

