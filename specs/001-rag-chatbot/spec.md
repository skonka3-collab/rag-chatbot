# Feature Specification: Local RAG Chatbot

## User Story

As a user, I want to upload documents and ask questions about them so that I can
quickly find grounded answers with visible sources.

## Functional Requirements

- The app must accept PDF, TXT, and Markdown uploads.
- The app must extract text from uploaded documents.
- The app must split documents into searchable chunks.
- The app must retrieve relevant chunks for a user question.
- The app must answer using retrieved document content.
- The app must show citations or source previews for retrieved passages.

## Acceptance Criteria

- Given supported documents are uploaded, when the user builds the index, then the
  app makes the documents searchable.
- Given an indexed knowledge base, when the user asks a question, then the app
  returns an answer grounded in relevant source passages.
- Given no relevant source passage exists, when the user asks a question, then the
  app explains that the documents do not contain enough information.

## Constraints

- The app runs locally.
- The app does not require an external AI API key.
- Scanned PDFs require OCR before reliable extraction.

