# Skill

## Name

Local Document RAG Chatbot

## Purpose

Build and run a local retrieval chatbot that can answer questions from user-uploaded documents.

## Inputs

- PDF files with selectable text
- TXT files
- Markdown files
- User questions

## Process

1. Extract text from each uploaded file.
2. Normalize whitespace.
3. Split text into overlapping chunks.
4. Tokenize the question and chunks.
5. Score chunks by query overlap and token frequency.
6. Use the highest-scoring chunks to produce a grounded answer.
7. Display source previews so the user can verify the answer.

## Output

- Chat answer grounded in uploaded documents
- Source citations
- Retrieved source previews

## Dependencies

- Streamlit
- PyPDF2
