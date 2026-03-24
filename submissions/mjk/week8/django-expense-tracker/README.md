# Expense Tracker — Django + Vanilla JS + SQLite

A personal expense tracking web application built with Django and plain JavaScript. This is the Python-based version of the multi-stack expense tracker project.

## Features

- Create, read, update, and delete income/expense transactions
- Fixed categories for expenses (식비, 교통, 쇼핑, 주거, 여가, 기타) and income (급여, 용돈, 기타수입)
- Monthly summary with total income, total expenses, and net balance
- Interactive charts: category breakdown (pie chart) and income vs. expense comparison (bar chart)
- Filter transactions by month, category, and type
- Responsive single-page UI

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation & Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Seed the database with sample data (13 transactions across 2 months)
python manage.py seed
```

## Running the Application

```bash
python manage.py runserver
```

Open your browser and navigate to **http://localhost:8000**

## Project Structure

```
django-expense-tracker/
├── config/                  # Django project configuration
│   ├── settings.py          # Database, static files, installed apps
│   └── urls.py              # URL routing (API + static serving)
├── tracker/                 # Main application
│   ├── models.py            # Transaction model (Django ORM)
│   ├── views.py             # API views (CRUD, summary, categories)
│   └── management/
│       └── commands/
│           └── seed.py      # Database seeding command
├── static/                  # Frontend (served by Django)
│   ├── index.html           # Single-page application shell
│   ├── app.js               # Vanilla JS (API calls, DOM manipulation, charts)
│   └── styles.css           # Responsive CSS
├── requirements.txt         # Python dependencies
└── README.md
```

## API Endpoints

| Method | Endpoint                    | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/api/transactions`         | List transactions (query: month, category, type) |
| POST   | `/api/transactions`         | Create a new transaction                 |
| PATCH  | `/api/transactions/<id>`    | Update a transaction (partial)           |
| DELETE | `/api/transactions/<id>`    | Delete a transaction                     |
| GET    | `/api/summary`              | Monthly summary with category breakdown  |
| GET    | `/api/categories`           | List available categories by type        |

## Tech Stack

| Layer      | Technology                |
|------------|---------------------------|
| Backend    | Django 5.x (Python)       |
| Frontend   | Vanilla JavaScript (ES6+) |
| Charts     | Chart.js 4.x (via CDN)   |
| Database   | SQLite3                   |
| Styling    | Plain CSS (no framework)  |

## Known Issues & Notes

- CSRF protection is disabled on API endpoints (`@csrf_exempt`) since there is no authentication layer. In a production app, proper CSRF tokens or token-based auth (JWT) should be used.
- The application uses Django's development server (`runserver`), which is not suitable for production. Use Gunicorn + Nginx for deployment.
- SQLite database file (`db.sqlite3`) is created automatically on first migration.
