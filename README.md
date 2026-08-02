# mintaj

Backend API for registering/logging in via social accounts (Google Sign-In, Discord OAuth2) and issuing JWT tokens.

**Stack:** Python 3.14, Django 6+, [django-ninja](https://django-ninja.dev/) (HTTP layer, no DRF),
[django-ninja-jwt](https://github.com/eadwinCode/django-ninja-jwt) (auth), PostgreSQL (`psycopg2`), Poetry.
Served via `gunicorn` + `whitenoise` (static files), config loaded through `python-dotenv`.

Dev tooling: `black`, `isort`, `flake8`, `pylint`, `bandit` (linting), `pytest-django` + `pytest-factoryboy` +
`factory-boy` + `freezegun` (testing), `pre-commit`.

## Getting started

```bash
poetry install
cp .env.local .env   # or export the variables below directly
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Required environment variables (see `.env.local` / `.env.test_ci` for local/test values):

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `STATIC_URL` | Django core settings |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |
| `GOOGLE_CLIENT_ID` | Verifies Google Sign-In ID tokens (`api/users/router.py::google_login`) |
| `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI` | Discord OAuth2 authorization code flow |

## Commands

```bash
make test    # pytest, settings=config.settings.test
make lint    # isort, black, flake8, pylint, bandit
make all     # lint + test
```