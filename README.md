# RAG Chatbot

A local Streamlit chatbot that answers questions from uploaded PDF, TXT, or
Markdown files.

## Features

- Local document question answering for PDF, TXT, and Markdown files
- Extractive retrieval-augmented generation without an external AI API key
- Source previews and citations for each grounded answer
- Configurable chunking logic for balancing context and relevance
- CI and pre-commit checks for formatting, linting, typing, tests, coverage, and
  security

The app uses a lightweight retrieval-augmented generation flow:

- Extract text from uploaded documents
- Split documents into overlapping chunks
- Retrieve the most relevant chunks for each question
- Generate an answer from the retrieved text
- Show citations and source previews

## Requirements

- Python 3.11 or later
- A terminal with `pip`
- Documents that contain selectable text

## Quick Start

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate     # Windows
```

2. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

4. Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Usage

1. Upload one or more PDF, TXT, or Markdown files from the sidebar.
2. Click **Build / Refresh Index**.
3. Enter a question in the chat box.
4. Review the generated answer and cited source passages.

## Notes

This version runs without an external AI API key. It creates grounded extractive
answers from the uploaded documents. For scanned PDFs, use OCR first so the PDF
contains selectable text.

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests and checks:

```bash
ruff format --check .
ruff check .
mypy .
pytest --cov=app --cov-report=term-missing
```

Run security and audit checks:

```bash
detect-secrets-hook --baseline .secrets.baseline --exclude-files .secrets.baseline $(git ls-files)
python -m pip_audit -r requirements.txt --no-deps --disable-pip
bandit -q -r app.py
```

Run pre-commit hooks locally:

```bash
pre-commit install
pre-commit run --all-files
```

## Docker

Build and run the containerized app:

```bash
docker build -t rag-chatbot .
docker run --rm -p 8501:8501 rag-chatbot
```

Then open:

```text
http://localhost:8501
```

## Project Structure

```text
app.py                  Streamlit application and RAG helpers
tests/                  Unit tests for extraction, retrieval, and answer logic
specs/                  Spec Kit feature specifications and implementation plans
.specify/               Spec Kit constitution and templates
.gitlab-ci.yml          GitLab CI quality and security pipeline
.pre-commit-config.yaml Local pre-commit quality checks
```

## Security

The app processes uploaded documents locally and does not require external AI API
calls. Do not commit private documents, secrets, `.env` files, or generated
indexes. See [SECURITY.md](SECURITY.md) for responsible disclosure guidance.

## License

This project is licensed under the GNU Affero General Public License v3.0 or
later. See [LICENSE](LICENSE) for the full license text.

