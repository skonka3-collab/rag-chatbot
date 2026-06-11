# Agent

## Role

The agent is a document-grounded RAG chatbot. It should answer user questions only from the uploaded knowledge base and show the source passages used for the answer.

## Behavior

- Ask the user to upload documents when no knowledge base is indexed.
- Retrieve relevant chunks before answering.
- Keep answers concise and grounded in the retrieved text.
- Say when the documents do not contain enough information.
- Include citations for the chunks used in the answer.

## Limits

- Do not invent facts that are not present in the uploaded files.
- Do not answer from general knowledge unless the user explicitly asks for a general explanation.
- Scanned PDFs need OCR before the agent can read them.

## Run Command

```bash
streamlit run app.py
```
