# CLAUDE.md — Week 4 Starter App Guide

## Quick Start

```bash
cd submissions/swk/week4
conda activate cs146s
make run          # http://localhost:8000 (frontend) | /docs (Swagger)
make test         # pytest -q backend/tests
make format       # black + ruff --fix
make lint         # ruff check
make seed         # seed SQLite DB
```

## Code Navigation

| Layer | Path | Role |
|-------|------|------|
| Entry point | `backend/app/main.py` | FastAPI app, mounts routers & static files |
| Database | `backend/app/db.py` | SQLAlchemy engine, `get_db` dependency, seed logic |
| ORM Models | `backend/app/models.py` | `Note(id, title, content)`, `ActionItem(id, description, completed)` |
| Schemas | `backend/app/schemas.py` | Pydantic v2 — `NoteCreate`, `NoteRead`, `ActionItemCreate`, `ActionItemRead` |
| Routers | `backend/app/routers/notes.py` | `GET /notes/`, `POST /notes/`, `GET /notes/search/`, `GET /notes/{id}` |
| Routers | `backend/app/routers/action_items.py` | `GET /action-items/`, `POST /action-items/`, `PUT /action-items/{id}/complete` |
| Services | `backend/app/services/extract.py` | `extract_action_items(text)` — parses `TODO:` and `!` lines |
| Frontend | `frontend/index.html`, `app.js`, `styles.css` | Vanilla HTML/JS, served at `/static` |
| Seed data | `data/seed.sql` | Initial schema + sample notes/action items |
| Tests | `backend/tests/` | `conftest.py` (temp SQLite fixture), `test_notes.py`, `test_action_items.py`, `test_extract.py` |
| Tasks | `docs/TASKS.md` | 7 feature tasks for extending the app |

## Architecture Pattern

```
Request → FastAPI Router → Service (optional) → SQLAlchemy Model → DB
                ↕
          Pydantic Schema (validation & serialization)
```

- Dependency injection: `db: Session = Depends(get_db)`
- Session lifecycle: auto-commit on success, rollback on exception, always closed
- Responses use `NoteRead.model_validate(orm_object)` for ORM → Pydantic conversion

## Style & Safety Guardrails

### Must follow:
- **Line length**: 100 characters (black + ruff)
- **Imports**: sorted by ruff (isort rules via `I`)
- **Type hints**: use on all function signatures
- **Status codes**: `201` for POST creation, `404` for not found, `200` for success
- **Pydantic v2**: use `model_validate()`, not deprecated `from_orm()`
- **SQLAlchemy 2.0**: use `select()` style, not legacy `query()`

### Safe commands (OK to run freely):
```bash
make test       # isolated temp DB, no side effects
make format     # auto-fixes style only
make lint       # read-only check
```

### Avoid:
- Do NOT modify `pyproject.toml`, `Makefile`, or `conftest.py` unless explicitly asked
- Do NOT delete `data/seed.sql` or `data/app.db`
- Do NOT install new dependencies without asking

## Workflow: Adding a New Endpoint

When asked to add a new API endpoint, follow this order:

1. **Write a failing test first** in `backend/tests/test_<resource>.py`
2. **Add Pydantic schema** (if needed) in `backend/app/schemas.py`
3. **Update ORM model** (if needed) in `backend/app/models.py`
4. **Implement the router** in `backend/app/routers/<resource>.py`
5. **Run tests**: `make test` — ensure the new test passes
6. **Run lint**: `make format && make lint` — ensure style compliance
7. **Update frontend** (if needed) in `frontend/app.js` and `frontend/index.html`

## Workflow: Adding a New Model/Resource

1. Define the model in `backend/app/models.py` (extend `Base`)
2. Add Create/Read schemas in `backend/app/schemas.py`
3. Create router file in `backend/app/routers/<resource>.py`
4. Register router in `backend/app/main.py` via `app.include_router()`
5. Add seed data in `data/seed.sql` (optional)
6. Write tests in `backend/tests/test_<resource>.py`
7. Run: `make test && make format && make lint`

## Current Gaps (see docs/TASKS.md)

- Notes: missing PUT (edit) and DELETE endpoints
- Search: case-sensitive (should be case-insensitive)
- Extraction service: not exposed as an API endpoint
- Validation: no min-length checks on schemas
- Docs: no `API.md` documenting endpoints
