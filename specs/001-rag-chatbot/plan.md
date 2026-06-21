# Implementation Plan: Local RAG Chatbot

## Summary

Build a local Streamlit app that indexes uploaded documents and answers user
questions from retrieved source passages.

## Technical Context

- Language: Python 3.11
- UI framework: Streamlit
- Supported inputs: PDF, TXT, Markdown
- Testing: pytest with coverage
- Quality gates: ruff, flake8, pylint, mypy, vulture, pyupgrade, bandit, semgrep,
  detect-secrets, pip-audit

## Implementation Steps

1. Extract text from supported uploaded documents.
2. Split extracted text into overlapping chunks.
3. Score chunks against the user question.
4. Generate grounded extractive answers from the highest scoring chunks.
5. Render citations and source previews in the Streamlit interface.
6. Cover core behavior with unit tests and CI quality checks.

## Validation

- Run formatting and lint checks.
- Run type checking.
- Run tests with coverage.
- Run secret scanning, dependency audit, and static security checks.

