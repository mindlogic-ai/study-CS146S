# CLAUDE.md -- Week 4 Project Context

## Project Overview
Notes + Action Items full-stack app.
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Vanilla JS SPA served via FastAPI static mount
- Tests: pytest with temp-DB fixture

## Directory Layout
```
week4/
  backend/
    app/
      main.py          # FastAPI app, startup event, router includes
      db.py            # SQLAlchemy engine (SQLite), get_db dependency, seeding
      models.py        # Note(id, title, content), ActionItem(id, description, completed)
      schemas.py       # Pydantic v2: NoteCreate, NoteRead, ActionItemCreate, ActionItemRead
      routers/
        notes.py       # GET /notes/, POST /notes/, GET /notes/search/?q=, GET /notes/{id}
        action_items.py # GET /action-items/, POST /action-items/, PUT /action-items/{id}/complete
      services/
        extract.py     # extract_action_items(text) -- parses lines ending ! or starting TODO:
    tests/
      conftest.py      # client fixture: temp SQLite DB, dependency override
      test_notes.py
      test_action_items.py
      test_extract.py
  frontend/
    index.html, app.js, styles.css
  data/
    seed.sql           # DDL + sample data
  docs/
    TASKS.md           # Enhancement task list
  Makefile             # run, test, format, lint, seed
```

## How to Run
All commands run from the `week4/` directory with `conda activate cs146s`.
- `make run`    -- starts uvicorn on :8000 (PYTHONPATH=.)
- `make test`   -- runs pytest -q backend/tests (PYTHONPATH=.)
- `make format` -- black . && ruff check . --fix
- `make lint`   -- ruff check .
- `make seed`   -- applies data/seed.sql

## Database Schema (SQLite)
- **notes**: id INTEGER PK AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL
- **action_items**: id INTEGER PK AUTOINCREMENT, description TEXT NOT NULL, completed BOOLEAN NOT NULL DEFAULT 0

## Style and Safety Guardrails
- Formatter: black
- Linter: ruff
- Python target: 3.10+
- ALWAYS run `make format` then `make lint` after code changes
- ALWAYS run `make test` before considering work complete
- NEVER modify data/app.db directly; use seed.sql or API
- NEVER commit .env files or secrets

## Workflow Patterns

### Adding a new endpoint
1. Write a failing test in backend/tests/test_<module>.py
2. Add/update the Pydantic schema in schemas.py if needed
3. Add/update the SQLAlchemy model in models.py if needed
4. Implement the route in the appropriate router file
5. Run `make test` -- confirm the new test passes and no existing tests break
6. Run `make format && make lint` -- fix any issues
7. Update frontend/app.js if the endpoint has UI implications

### Adding validation
1. Write a test that sends invalid data and asserts 422 or 400
2. Add Field() constraints or validators to schemas.py
3. Run `make test`

### Modifying the extraction service
1. Write a test in test_extract.py with the new expected behavior
2. Update extract.py
3. Run `make test`

## Known Issues
- Search (`/notes/search/?q=`) is case-sensitive due to SQLite `.contains()` behavior
- No input validation -- empty strings accepted for title/content/description
- No PUT/DELETE for notes
- No tag extraction (#tag parsing) in extract.py
- No docs/API.md

## Testing Conventions
- Fixture `client` provides a TestClient with a fresh temp SQLite DB
- Test files: `backend/tests/test_<module>.py`
- Run with: `PYTHONPATH=. pytest -q backend/tests`
