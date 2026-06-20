# Security Policy

## Supported Versions

The `main` branch receives security fixes.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately to the project maintainer through GitLab. Include:

- Affected files or features
- Steps to reproduce
- Expected impact
- Suggested fix, if known

Do not open public issues for unpatched vulnerabilities.

## Security Checks

CI runs secret scanning, dependency auditing, and a Python security scan with:

```bash
detect-secrets-hook --baseline .secrets.baseline --exclude-files .secrets.baseline $(git ls-files)
python -m pip_audit -r requirements.txt --no-deps --disable-pip
bandit -q -r app.py
```
