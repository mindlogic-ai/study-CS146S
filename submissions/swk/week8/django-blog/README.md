# Django Blog

A blog application built with **Django** + **Django REST Framework** and a **Vanilla JS** frontend.

## Tech Stack

- **Backend:** Python / Django 6.0 / Django REST Framework
- **Frontend:** Vanilla HTML / CSS / JavaScript
- **Database:** SQLite

## Prerequisites

- Python 3.10+
- pip

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List all posts (supports `?search=`) |
| POST | `/api/posts/` | Create a new post |
| GET | `/api/posts/:id/` | Get a single post |
| PUT | `/api/posts/:id/` | Update a post |
| DELETE | `/api/posts/:id/` | Delete a post |

## Features

- Create, read, update, and delete blog posts
- Search posts by title, content, author, or tags
- Tag support (comma-separated)
- Responsive UI
