# RAG Chatbot

A self-contained, local Streamlit application for **Retrieval-Augmented Generation (RAG)** over uploaded documents.

## What is Retrieval-Augmented Generation?

Retrieval-Augmented Generation is a technique that combines document retrieval with answer generation to produce grounded, context-aware responses. Instead of relying solely on a pre-trained language model, RAG:

1. Retrieves the most relevant passages from a document corpus
2. Uses those passages as context to generate accurate, cited answers
3. Ensures all answers are grounded in source material

This RAG Chatbot application implements this workflow entirely **locally**—no external AI API keys required. It extracts text from PDF, TXT, and Markdown files, indexes them for fast retrieval, and generates answers with full source citations.

## Features

- **Multi-Format Document Support** — Upload and process PDF, TXT, and Markdown files
- **Extractive Question Answering** — Generate grounded answers directly from document content
- **No External Dependencies** — Runs entirely locally without requiring external AI APIs or authentication keys
- **Source Citations** — Every answer includes the original source passages and document references
- **Semantic Chunking** — Intelligently splits documents into overlapping chunks to preserve context
- **Interactive UI** — User-friendly Streamlit interface for uploading documents and asking questions
- **Production-Ready Quality Checks** — Automated code formatting, linting, type checking, and security scanning via pre-commit hooks
- **CI/CD Pipeline** — GitLab CI configuration for automated testing, coverage reporting, and security audits
- **Comprehensive Testing** — Unit tests for document extraction, text retrieval, and answer generation

## System Requirements

- **Python 3.11** or later
- **pip** (Python package manager)
- **Git** (for version control)
- Documents containing **selectable text** (not scanned images without OCR)
- Approximately 500 MB of disk space for dependencies

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://code.swecha.org/saisandeep_konka/rag-chatbot.git
cd rag-chatbot
```

### 2. Create a Python Virtual Environment

A virtual environment isolates this project's dependencies from your system Python.

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Git Bash):**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import streamlit; print(f'Streamlit {streamlit.__version__} installed successfully')"
```

## Usage

### Running the Application

```bash
streamlit run app.py
```

Streamlit will start a local web server and display the URL (typically `http://localhost:8501`). Open this URL in your web browser.

### How to Use the Interface

1. **Upload Documents** — Use the sidebar to upload one or more PDF, TXT, or Markdown files
2. **Build Index** — Click "Build / Refresh Index" to process the documents
3. **Ask Questions** — Enter a question in the chat box
4. **Review Results** — The chatbot returns:
   - A grounded answer based on the document content
   - Original source passages that support the answer
   - Links to the documents cited

### Example Questions

- "What is the main topic of this document?"
- "Summarize the key findings."
- "What are the limitations mentioned?"

## Development & Code Quality

### Install Development Dependencies

Development dependencies include tools for formatting, linting, type checking, testing, and security scanning.

```bash
pip install -r requirements-dev.txt
```

### Running Pre-Commit Hooks

Pre-commit hooks automatically run quality checks before each commit. Install and run them:

```bash
pre-commit install
pre-commit run --all-files
```

This will run:
- **Ruff** — Code formatting and linting
- **MyPy** — Static type checking
- **Pytest** — Unit tests with coverage
- **Bandit** — Security vulnerability scanning
- **Detect-Secrets** — Secret detection
- **Pip-Audit** — Dependency vulnerability auditing
- **Flake8, Pylint, Vulture** — Additional code quality checks
- **PyUpgrade** — Python syntax modernization
- **Semgrep** — Static analysis (Linux/macOS only)

### Running Checks Individually

**Code Formatting:**
```bash
ruff format .
```

**Code Linting:**
```bash
ruff check .
```

**Type Checking:**
```bash
mypy .
```

**Unit Tests:**
```bash
pytest --cov=app --cov-report=term-missing
```

**Security Scanning:**
```bash
bandit -q -r app.py
detect-secrets-hook --baseline .secrets.baseline --exclude-files .secrets.baseline $(git ls-files)
python -m pip_audit -r requirements.txt --no-deps --disable-pip
```

### Skipping Specific Checks (Windows)

On Windows, `semgrep` may not be available. To skip it:

```bash
SKIP=semgrep pre-commit run --all-files
```

## Project Structure

```
rag-chatbot/
├── app.py                    # Main Streamlit application and RAG implementation
├── tests/                    # Unit tests for core functionality
│   └── test_app.py          # Tests for document processing, retrieval, and answers
├── specs/                    # Project specifications and feature documentation
│   └── 001-rag-chatbot/     # Detailed spec for the RAG chatbot feature
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development and CI/CD dependencies
├── .pre-commit-config.yaml   # Pre-commit hook configuration
├── .gitlab-ci.yml            # GitLab CI/CD pipeline configuration
├── pyproject.toml            # Python project metadata and tool configurations
├── LICENSE                   # GNU AGPL v3.0 license
├── SECURITY.md              # Security policy and responsible disclosure
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

## Docker Support

### Build the Docker Image

```bash
docker build -t rag-chatbot:latest .
```

### Run the Application in Docker

```bash
docker run --rm -p 8501:8501 rag-chatbot:latest
```

Then open `http://localhost:8501` in your browser.

## Security & Privacy

- **Local Processing** — All document processing happens on your machine; no data is sent to external servers
- **No API Keys Required** — This application does not depend on external AI APIs
- **Secret Protection** — Secrets are automatically detected and prevented from being committed
- **Dependency Auditing** — All dependencies are audited for known vulnerabilities

**Important:** Do not commit:
- Private documents
- Credentials or `.env` files
- Generated vector indexes
- Any sensitive data

For responsible disclosure of security issues, see [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to your fork (`git push origin feature/your-feature`)
5. Open a Pull Request

All commits must pass the pre-commit checks. Run `pre-commit run --all-files` before pushing.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** or later. This means:

- You can use, modify, and distribute this software
- You must include a copy of the license
- If you distribute this software or modifications, you must make the source code available
- If you use this software in a network application, users accessing it must be able to download the source code

See [LICENSE](LICENSE) for the full legal text.

## Troubleshooting

### "Executable `semgrep` not found" on Windows

Semgrep is not yet supported on Windows via pip. Either:
- Use WSL (Windows Subsystem for Linux)
- Skip semgrep: `SKIP=semgrep pre-commit run --all-files`
- Run checks on Linux/macOS

### PDF Text Extraction Fails

Ensure your PDF contains **selectable text** (not just scanned images). For scanned PDFs:
- Use OCR software to convert the PDF to text-selectable format first
- Then upload the OCR'd PDF to the chatbot

### Virtual Environment Not Activating

Make sure you're using the correct activation command for your shell:
- **Bash/Zsh:** `source .venv/bin/activate`
- **PowerShell:** `.\.venv\Scripts\Activate.ps1`
- **Command Prompt:** `.venv\Scripts\activate.bat`

## Support & Questions

For questions, issues, or feature requests:
- Open an issue on the GitLab repository
- Review existing issues before creating a new one
- Provide details about your OS, Python version, and any error messages

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes and version history.

# ci trigger
