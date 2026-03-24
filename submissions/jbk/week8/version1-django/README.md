# Version 1: Django + Django REST Framework + Vanilla JS

## Tech Stack
- **Backend:** Python / Django 5.x / Django REST Framework
- **Frontend:** Vanilla HTML / CSS / JavaScript
- **Database:** SQLite (Django default)

## Prerequisites
- Python 3.10+
- pip

## Installation & Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed sample data
python manage.py seed
```

## Run

```bash
python manage.py runserver 8000
```

Visit http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notes/ | List notes (query: q, skip, limit, sort) |
| POST | /api/notes/ | Create note |
| GET | /api/notes/:id/ | Get note |
| PATCH | /api/notes/:id/ | Update note |
| GET | /api/action-items/ | List items (query: completed, skip, limit, sort) |
| POST | /api/action-items/ | Create item |
| GET | /api/action-items/:id/ | Get item |
| PATCH | /api/action-items/:id/ | Update item |
| PUT | /api/action-items/:id/complete/ | Mark complete |
