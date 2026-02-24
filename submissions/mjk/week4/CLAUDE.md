# Week 4 - Developer Command Center

FastAPI + SQLite starter app for CS146S Week 4.

## Project Structure

```
backend/app/
  main.py           - FastAPI entry point, mounts static files, registers routers
  db.py             - SQLAlchemy engine/session, auto-seed logic
  models.py         - ORM models: Note, ActionItem
  schemas.py        - Pydantic request/response schemas
  routers/
    notes.py        - GET/POST /notes/, GET /notes/search/, GET /notes/{id}
    action_items.py - GET/POST /action-items/, PUT /action-items/{id}/complete
  services/
    extract.py      - extract_action_items() text parsing
backend/tests/
  conftest.py       - client fixture (TestClient + temp SQLite DB)
  test_notes.py, test_action_items.py, test_extract.py
frontend/           - Static HTML/JS/CSS (vanilla, no framework)
data/seed.sql       - Initial seed data
docs/TASKS.md       - Development task backlog
```

## Commands (run from submissions/mjk/week4/)

- `make run` — Start server at http://localhost:8000
- `make test` — Run pytest (`PYTHONPATH=. pytest -q backend/tests`)
- `make format` — black + ruff --fix
- `make lint` — ruff check
- `make seed` — Initialize DB with seed data

## Development Patterns

- **Adding an endpoint**: schema in `schemas.py` → router function → test in `backend/tests/` → `make format` → `make test`
- **Dependency injection**: `db: Session = Depends(get_db)` for DB sessions
- **Response codes**: 201 for creation, 200 for reads/updates, 404 for not found
- **ORM style**: SQLAlchemy 2.0 (`select()`, `db.execute()`)

## Code Style

- Line length: 100 (black + ruff)
- Rules: E, F, I, UP, B (see pyproject.toml)
- All imports at top of file

## Custom Slash Commands

- `/test-and-fix` — Automated test → analyze → fix → format → retest loop
- `/docs-sync` — Sync `docs/API.md` from OpenAPI spec, show route deltas

## Safety

- Safe to run: `make test`, `make format`, `make lint`
- Don't modify test files when fixing failures — fix the implementation
- Don't delete `data/app.db` without confirmation
