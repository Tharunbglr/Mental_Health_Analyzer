# Mental Health Analyzer

A Flask web app that provides mental health screenings (PHQ-9 and GAD-7) with safe, personalized suggestions. Features optional AI-assisted insights via OpenAI, with strong privacy controls and crisis resources.

## Important Disclaimers

⚠️ **This is not a medical tool or diagnostic device**
- For informational purposes only
- Not a substitute for professional medical advice
- If in crisis, contact emergency services immediately
- Always consult qualified healthcare professionals

🔒 **Privacy & Data Safety**
- No persistent data storage by default
- Optional AI processing with strict data sanitization
- Crisis resources provided but no emergency intervention
- See Privacy Policy for full details

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

## Deployment Guide

### Prerequisites
1. Python 3.9+ and pip
2. Redis (for rate limiting)
3. SSL certificate (recommended for production)
4. Secure key storage solution

### Production Setup
1. **Environment Configuration**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY="your-secure-key"  # Use a proper secret key generator
   export LOG_LEVEL=INFO
   export LOG_RETENTION_DAYS=30
   export RATELIMIT_DEFAULT="100/day"
   export RATELIMIT_STORAGE_URI="redis://localhost:6379/0"
   ```

2. **SSL Setup**
   - Use a reverse proxy (nginx/Apache) with SSL
   - Or configure with gunicorn/waitress behind CDN

3. **Monitoring**
   - Configure `/healthz` endpoint monitoring
   - Set up error alerting
   - Monitor rate limits and logs

4. **Security Checklist**
   - [ ] Secret key properly configured
   - [ ] Debug mode disabled
   - [ ] SSL/TLS enabled
   - [ ] Headers configured (CSP, HSTS)
   - [ ] Rate limiting active
   - [ ] Log rotation working
   - [ ] Firewall rules set
   - [ ] Dependencies up to date

### AI Integration Safety

1. **Data Sanitization**
   - Names removed
   - Free text truncated to 500 chars
   - Sensitive patterns filtered
   - No PII/PHI transmitted

2. **Rate Limiting**
   - AI requests: 50/day per IP
   - Form submissions: 100/day per IP
   - Burst protection enabled

3. **Fallback Mechanism**
   - Rule-based suggestions always available
   - Graceful AI failure handling
   - Clear user communication

4. **Configuration**
   ```bash
   export OPENAI_API_KEY="your-key"
   export OPENAI_MODEL="gpt-4o-mini"
   export AI_REQUEST_TIMEOUT=10
   export AI_MAX_RETRIES=2
   ```

## Privacy & Data Safety

### Data Handling
1. **Storage**
   - No persistent data by default
   - All analysis in-memory
   - Logs sanitized automatically
   - Optional AI processing with consent

2. **Logging Controls**
   - Sensitive fields masked
   - IP addresses anonymized
   - 30-day retention limit
   - Structured log format

3. **User Privacy**
   - Opt-in AI processing
   - Clear consent language
   - Privacy policy linked
   - Right to opt-out

4. **Crisis Protocol**
   - Emergency resources displayed
   - No medical advice given
   - Clear disclaimers
   - Local resources prioritized

### Compliance Notes
- Implement appropriate privacy policy
- Add Terms of Service
- Consider local regulations
- Document data flows
- Regular security audits
- Incident response plan

## Repository Structure

```
Mental_Health_Analyzer/
├── app/                    # Main application code
│   ├── static/            # CSS, JS, images
│   ├── templates/         # Jinja2 templates
│   ├── __init__.py       # App factory
│   ├── ai.py             # AI integration
│   ├── config.py         # Configuration
│   ├── health.py         # Health checks
│   ├── routes.py         # URL routes
│   └── utils.py          # Helper functions
├── tests/                 # Test suite
├── .github/              # GitHub Actions
├── instance/             # Instance config
├── docker/               # Docker configs
└── docs/                 # Documentation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guide
- PR process
- Testing requirements
- Security guidelines
