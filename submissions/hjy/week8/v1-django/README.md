# Notes & Action Items — Django + DRF

A simple CRUD app for managing notes and action items, built with Django 5.x and Django REST Framework.

## Prerequisites

- Python 3.12

## Setup

```bash
cd week8/v1-django

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Open http://localhost:8000 in your browser.

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/notes/` | List notes (`?q=` search, `?ordering=-created_at`) |
| POST | `/api/notes/` | Create note |
| GET | `/api/notes/{id}/` | Get note |
| PATCH | `/api/notes/{id}/` | Partial update note |
| DELETE | `/api/notes/{id}/` | Delete note |
| GET | `/api/action-items/` | List action items (`?completed=true/false`) |
| POST | `/api/action-items/` | Create action item |
| PATCH | `/api/action-items/{id}/` | Partial update |
| DELETE | `/api/action-items/{id}/` | Delete |

## Stack

- Django 5.x
- Django REST Framework 3.x
- SQLite (default)
- Vanilla JS frontend
