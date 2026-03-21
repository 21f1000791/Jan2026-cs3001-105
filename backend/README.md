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

Default seed accounts:

- admin: `admin@communityops.local` / `password123`
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
