# house_cleaner

This repository is a Django project prepared for local development and production deployment.

Quick start (local dev):

1. Create virtualenv and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env to set SECRET_KEY and other values
python manage.py migrate
python manage.py runserver
```

Run with Docker:

```powershell
docker compose up --build
```

Production (example): set `DJANGO_SETTINGS_MODULE=house_cleaner.settings.prod` and use a WSGI server such as Gunicorn.
