# d-money-tracker
MoneyTracker is a Django application, which is developed to maintain all expenses at one place

A production-ready **Django REST Framework** application with PostgreSQL, split settings, whitenoise static serving, and environment-based configuration.

---

## Project Layout

```
dmoneytracker/
├── pyproject.toml              # dependencies + project metadata
├── .env.example                # env-var template  →  copy to .env
├── .gitignore
├── manage.py                   # Django CLI entry-point
│
├── dmoneytracker/              # core Django package
│   ├── __init__.py
│   ├── urls.py                 # root URL config  (API lives at /api/)
│   ├── wsgi.py                 # gunicorn entry-point
│   ├── asgi.py                 # uvicorn / channels entry-point
│   └── settings/
│       ├── __init__.py
│       ├── base.py             # shared settings (DB, DRF, logging …)
│       ├── development.py      # DEBUG=True, verbose logging
│       └── production.py       # hardened security, compressed static
│
├── templates/
│   └── base.html               # global Django template skeleton
│
├── static/                     # source assets collected by whitenoise
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── media/                      # user-uploaded files (runtime, git-ignored)
└── logs/                       # django.log written here (git-ignored)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -e ".[dev]"
```

> The `[dev]` extras pull in `django-debug-toolbar` and `ipython`.
> For production only: `pip install -e .`

### 2. Create the environment file

```bash
cp .env.example .env
```

Open `.env` and fill in every value — at minimum:

| Variable | What to set |
|---|---|
| `SECRET_KEY` | A long random string (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `DB_USER` | Your PostgreSQL user |
| `DB_PASSWORD` | Your PostgreSQL password |
| `DB_NAME` | Name of the PostgreSQL database |

### 3. Create the PostgreSQL database

```bash
# Example using psql
sudo -u postgres psql -c "CREATE DATABASE dmoneytracker;"
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

The server starts at `http://127.0.0.1:8000`.
The DRF browsable API root is at `http://127.0.0.1:8000/api/`.

---

## Environment Switching

| Environment | `DJANGO_SETTINGS_MODULE` |
|---|---|
| Development | `dmoneytracker.settings.development` |
| Production | `dmoneytracker.settings.production` |

Set it in your shell **or** in your `.env` file:

```bash
export DJANGO_SETTINGS_MODULE=dmoneytracker.settings.production
```

---

## Production Deployment (gunicorn)

```bash
# Collect static files into staticfiles/ (served by whitenoise)
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn dmoneytracker.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile  logs/gunicorn-error.log
```

### Key production notes

- **Static files** are handled automatically by `whitenoise` (no nginx required for static).
- **Media files** (user uploads) should be served via your reverse proxy (nginx) or an object store (S3).
- **HTTPS** — `production.py` enables `SECURE_SSL_REDIRECT`. Terminate TLS at your reverse proxy or load balancer.
- **ALLOWED_HOSTS** — set to your actual domain(s) in `.env`.

---

## Tech Stack

| Layer | Package |
|---|---|
| Web framework | Django 5.1+ |
| API toolkit | Django REST Framework 3.15+ |
| Database driver | psycopg2-binary |
| Env variables | python-decouple |
| Static files | whitenoise (with brotli) |
| WSGI server | gunicorn |
| CORS | django-cors-headers |
| Image handling | Pillow |
