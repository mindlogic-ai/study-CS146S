# Notes & Action Items - Django Version

A full-stack Notes & Action Items manager built with Django + Django REST Framework + Vanilla JavaScript.

## Tech Stack

- **Backend:** Python 3.12, Django 6.x, Django REST Framework
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Database:** SQLite
- **Package Manager:** uv

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup & Run

```bash
# Install dependencies
uv sync

# Run database migrations
uv run python manage.py migrate

# (Optional) Create admin superuser
uv run python manage.py createsuperuser

# Start the development server
uv run python manage.py runserver
```

The app will be available at **http://localhost:8000**.

API browsable interface (DRF) at **http://localhost:8000/api/**.

## API Endpoints

| Method | Endpoint                  | Description            |
|--------|---------------------------|------------------------|
| GET    | /api/notes/               | List all notes         |
| POST   | /api/notes/               | Create a note          |
| GET    | /api/notes/{id}/          | Get a note             |
| PATCH  | /api/notes/{id}/          | Update a note          |
| DELETE | /api/notes/{id}/          | Delete a note          |
| GET    | /api/action-items/        | List all action items  |
| POST   | /api/action-items/        | Create an action item  |
| GET    | /api/action-items/{id}/   | Get an action item     |
| PATCH  | /api/action-items/{id}/   | Update an action item  |
| DELETE | /api/action-items/{id}/   | Delete an action item  |

### Query Parameters

- Notes: `?q=search_term` for search, `?sort=field` for sorting
- Action Items: `?completed=true` to filter by completion status

## Known Issues

- No authentication (development mode only)
- CORS is open for all origins (development only)
