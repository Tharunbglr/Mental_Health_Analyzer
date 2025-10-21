# Mental Health Analyzer

A Flask web app that collects a brief well-being check-in and returns safe, personalized suggestions. Optional AI-assisted insights via OpenAI.

## Features
- Modern dark UI with responsive layout
- Form validation, CSRF protection
- Security headers (CSP, HSTS), rate limiting
- Health check `/healthz`, custom 404/500
- Rotating file logs
- Optional AI enhancement (OpenAI)
- Dockerfile + Compose (Redis for rate limits)
- CI with GitHub Actions; tests via pytest

## AI Setup (optional)
- Set environment variable before running:
  - PowerShell: `$env:OPENAI_API_KEY = "sk-..."; $env:OPENAI_MODEL = "gpt-4o-mini"`
  - macOS/Linux: `export OPENAI_API_KEY=sk-...; export OPENAI_MODEL=gpt-4o-mini`
- Check the "Enhance suggestions using AI" box on the form.
- Safe prompting is used and a rule-based fallback remains.

## Local Dev (PowerShell)
```powershell
cd "C:\Users\user\Desktop\Mental Health Analyzer"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
$env:FLASK_ENV = "development"; $env:SECRET_KEY = "dev-secret-key"
python wsgi.py
```

## Docker
```bash
docker build -t mental-health-analyzer .
docker run -e FLASK_ENV=production -e SECRET_KEY="change-me" -p 8080:8080 mental-health-analyzer
```

## Tests & Lint
```bash
pytest -q
ruff check .
black --check .
isort --check-only .
```

## Env Vars
- `FLASK_ENV` development|production
- `SECRET_KEY` required in prod
- `OPENAI_API_KEY` optional to enable AI
- `OPENAI_MODEL` default gpt-4o-mini
- `RATELIMIT_DEFAULT`, `RATELIMIT_STORAGE_URI`
- `LOG_LEVEL`, `LOG_RETENTION_DAYS`

## Development
- Templates: `app/templates`
- Static: `app/static`
- Routes: `app/routes.py`
- Config: `app/config.py`

## Disclaimer
This tool is informational only and not medical advice. If in crisis, contact local emergency services.

## Privacy & AI data handling
- The app stores no personal data by default. If you enable AI-assisted suggestions, the app will send a sanitized, non-identifying summary of your responses to the configured AI provider. This excludes names and truncates free-text notes to 500 characters.
- Do not enter highly sensitive personal information into the free-text field; the app is not a secure medical record system.
- For production deployments, configure secure storage, access controls, and a privacy policy appropriate for your jurisdiction.

## Repository organization & contributions
- Consider adding a `CONTRIBUTING.md` with coding guidelines, and a `.github/workflows/ci.yml` to run tests on push/pull requests.
- Suggested repo layout: keep `app/` for the Flask application, `tests/` for tests, `.github/` for workflows, and `docs/` for policy and deployment notes.
- When pushing changes, use feature branches and open pull requests for review.
