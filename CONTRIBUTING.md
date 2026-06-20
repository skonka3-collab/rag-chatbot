# Contributing

Thanks for helping improve RAG Chatbot.

## Local Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

## Quality Checks

Run these before opening a merge request:

```bash
ruff format --check .
ruff check .
mypy .
pytest --cov=app --cov-report=term-missing
detect-secrets-hook --baseline .secrets.baseline --exclude-files .secrets.baseline $(git ls-files)
python -m pip_audit -r requirements.txt --no-deps --disable-pip
bandit -q -r app.py
```

## Merge Request Guidelines

- Keep changes focused and easy to review.
- Add or update tests for behavior changes.
- Do not commit secrets, generated caches, or local environment files.
- Update documentation when commands, workflows, or user-facing behavior change.
