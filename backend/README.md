# Community Operations Platform - Backend

Production-grade Flask backend scaffold for the Community Operations Platform.

## Setup

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

## Run API

```bash
python run.py
```

The API is expected to run on `http://127.0.0.1:5000` and use `/api` prefix.

## Seed Database (Recommended)

Use the idempotent seeder to create baseline users/tasks/notifications without duplicates:

```bash
python seed_db.py
```

Optional: wipe existing records first, then reseed:

```bash
python seed_db.py --wipe
```

Optional: recreate a fresh SQLite DB instance and seed from scratch:

```bash
python seed_db.py --reset-db --wipe
```

Default seed accounts:

- admin: `admin@gmail.com` / `admin`
- manager: `manager@communityops.local` / `password123`
- staff: `staff.one@communityops.local` / `password123`
- staff: `staff.two@communityops.local` / `password123`

## Migrations

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

A placeholder migration structure is included under `migrations/`.

## Test

```bash
pytest -q
```

Note: local smoke scripts (such as `smoke_test_api.py`) create test data for validation.
For stable development data, use `seed_db.py` instead.

## Celery Worker

```bash
celery -A celery_worker.celery worker --loglevel=info
```

## Celery Beat (for periodic jobs in next steps)

```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Translations

Note: To enable UI translations, task translations and chatbot feature for managers follow the below steps.
To utilize the AI features in this platform, you will need to generate API keys for Sarvam AI and Groq (for Meta models) and add them to your newly created .env file.

1. Sarvam AI API Key
Go to the Sarvam AI Platform.
dashboard.sarvam.ai

Create an account or log in with your existing credentials.

Navigate to the API Keys section from your dashboard.

Generate a new API key and copy it to your clipboard.

2. Groq API Key (for Meta models)
Go to the Groq Cloud Console.
https://console.groq.com/home

Create an account or log in.

In the left-hand navigation menu, select API Keys.

Click Create API Key, give it a recognizable name (e.g., community-ops-dev), and copy the generated key.

3. Update .env
Open your .env file and append the following variables, replacing the placeholder text with the actual keys you just copied:

Code snippet
SARVAM_API_KEY=your_sarvam_api_key_here
GROQ_API_KEY=your_groq_api_key_here
