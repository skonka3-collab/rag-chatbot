# Agents

## RAG Chatbot Agent

The primary agent is a document-grounded assistant that answers questions using the
documents uploaded by the user.

## Responsibilities

- Prompt the user to upload documents when no index is available.
- Extract and chunk text from supported document types.
- Retrieve relevant chunks before answering a question.
- Keep answers concise and grounded in retrieved source text.
- Show citations and source previews for the answer.
- State clearly when the uploaded documents do not contain enough information.

## Boundaries

- Do not invent facts that are absent from the uploaded documents.
- Do not rely on general knowledge unless the user explicitly asks for it.
- Treat scanned PDFs as unsupported until OCR has been applied.

## Run Command

```bash
streamlit run app.py
```

