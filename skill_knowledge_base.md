# Skill

## Name

Knowledge Base QA Chatbot

## Purpose

Answer questions from an internal knowledge base by retrieving and synthesizing information from indexed documents.

## Inputs

- Company policy documents
- Product manuals
- FAQ pages
- User queries

## Process

1. Index documents and metadata from the knowledge base.
2. Normalize text and extract meaningful sections.
3. Generate vector embeddings for search.
4. Match the user query to the most relevant documents.
5. Retrieve top results and construct a concise answer.
6. Provide citations for the sources used.

## Output

- Direct answer drawn from knowledge base content
- Relevant document citations
- Recommended next steps or links

## Dependencies

- Sentence Transformers
- FAISS
