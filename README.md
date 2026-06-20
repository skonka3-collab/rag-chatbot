# RAG Chatbot

A local Streamlit chatbot that answers questions from uploaded PDF, TXT, or Markdown files.

The app uses a lightweight retrieval-augmented generation flow:

- Extract text from uploaded documents
- Split documents into overlapping chunks
- Retrieve the most relevant chunks for each question
- Generate an answer from the retrieved text
- Show citations and source previews

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## How to Use

1. Upload one or more PDF, TXT, or Markdown files from the sidebar.
2. Click **Build / Refresh Index**.
3. Ask questions in the chat box.
4. Review the answer and retrieved source passages.

## Notes

This version runs without an external AI API key. It creates grounded extractive answers from the uploaded documents. For scanned PDFs, use OCR first so the PDF contains selectable text.

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the quality checks used by CI:

```bash
ruff format --check .
ruff check .
mypy .
pytest --cov=app --cov-report=term-missing
detect-secrets-hook --baseline .secrets.baseline --exclude-files .secrets.baseline $(git ls-files)
python -m pip_audit -r requirements.txt --no-deps --disable-pip
```

Pre-commit can run the same checks before each commit:

```bash
pre-commit install
pre-commit run --all-files
```

## License

This project is licensed under the GNU Affero General Public License v3.0 or later. See [LICENSE](LICENSE) for the full license text.
