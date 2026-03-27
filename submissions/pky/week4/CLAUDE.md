# CLAUDE.md - Week 4 FastAPI Starter App

## Project Overview

Developer's command center — FastAPI backend with SQLite database and static HTML/JS frontend.
Located in `week4/` directory. Demonstrates RESTful API patterns with notes and action items.

## Structure

```
backend/app/main.py       — FastAPI app entry point
backend/app/db.py          — SQLAlchemy engine/session (SQLite)
backend/app/models.py      — ORM models (Note, ActionItem)
backend/app/schemas.py     — Pydantic v2 request/response schemas
backend/app/routers/       — notes.py, action_items.py
backend/app/services/      — extract.py (text extraction)
backend/tests/             — pytest tests with TestClient
frontend/                  — Static HTML/JS/CSS served via /static
data/                      — SQLite DB + seed.sql
docs/                      — API documentation
```

## Commands (all from week4/ directory)

```bash
make run      # Start server at localhost:8000
make test     # Run pytest
make format   # black + ruff --fix
make lint     # ruff check
make seed     # Seed database
```

## Architecture Pattern

```
FastAPI → Routers → Services → SQLAlchemy Models
                 ↓
         Pydantic Schemas (validation)
```

Request/response validation happens at router layer. Business logic lives in services.

## Coding Conventions

- **Line length:** 100 characters
- **Formatter:** black
- **Linter:** ruff (rules: E, F, I, UP, B)
- **Python:** 3.10+ (3.12 recommended)
- **Pydantic v2:** Use `model_validate()`, `from_attributes = True` in Config
- **Dependency injection:** `Depends(get_db)` for database sessions
- **HTTP status codes:** 201 for creation, 404 for not found, 422 for validation errors

## Test Pattern

- `conftest.py` creates temporary SQLite DB per test session
- Fixture name: `client` (FastAPI TestClient)
- Import models/schemas as needed
- No manual DB setup required — fixtures handle it

Example:
```python
def test_create_note(client):
    response = client.post("/notes/", json={"title": "Test", "content": "Body"})
    assert response.status_code == 201
```

## Workflow: Adding an Endpoint

1. Add schema to `schemas.py` if needed (Pydantic models)
2. Write a failing test in `backend/tests/`
3. Implement router in `backend/app/routers/`
4. Add service logic in `backend/app/services/` if complex
5. Run `make test` to verify
6. Run `make format` then `make lint`

## Safe Commands

Allowlisted: `make run`, `make test`, `make format`, `make lint`, `make seed`, `pytest`, `uvicorn`
