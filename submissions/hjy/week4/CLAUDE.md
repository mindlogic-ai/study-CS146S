# Week 4 — Developer's Command Center

## Quick Start

```bash
conda activate cs146s
make run      # http://localhost:8000 (frontend), /docs (Swagger)
make test     # pytest -q backend/tests
make format   # black + ruff --fix
make lint     # ruff check
make seed     # seed SQLite DB
```

## Project Structure

```
backend/
  app/
    main.py              # FastAPI entry, mounts static + routers
    db.py                # SQLAlchemy engine, get_db(), auto-seed
    models.py            # Note, ActionItem (SQLAlchemy ORM)
    schemas.py           # Pydantic v2 request/response models
    routers/
      notes.py           # /notes CRUD + search
      action_items.py    # /action-items CRUD + complete
    services/
      extract.py         # extract_action_items() from text
  tests/
    conftest.py          # tmp SQLite DB fixture
    test_notes.py
    test_action_items.py
    test_extract.py
frontend/
  index.html, app.js, styles.css   # static UI served at /static
data/
  seed.sql               # initial notes + action items
```

## Architecture

```
Request → FastAPI Router → SQLAlchemy Model → Pydantic Schema → Response
                ↓
          Depends(get_db)  # session injection
```

- SQLAlchemy 2.0: `select()` syntax, `db.get(Model, id)`
- Pydantic v2: `model_validate()`, `from_attributes = True`
- HTTP codes: 201 (created), 200 (ok), 404 (not found)

## Code Style

- Line length: 100 (pyproject.toml)
- Formatter: black
- Linter: ruff (rules: E, F, I, UP, B)
- Run `make format && make lint` before committing

## Testing

- pytest + httpx TestClient
- Temp SQLite DB per test session (conftest.py)
- Pattern: create via POST → verify via GET → test edge cases
