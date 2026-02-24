# Week 4 — Developer's Command Center

## Project Structure
```
backend/app/main.py        → FastAPI entry point, mounts routers & static files
backend/app/db.py           → SQLAlchemy engine, session management, seeding
backend/app/models.py       → ORM models: Note, ActionItem
backend/app/schemas.py      → Pydantic v2 request/response schemas
backend/app/routers/        → Endpoint handlers (notes.py, action_items.py)
backend/app/services/       → Business logic (extract.py)
backend/tests/              → Pytest suite with isolated SQLite fixture
frontend/                   → Static HTML/JS/CSS served at /static
data/seed.sql               → Initial database seed
docs/                       → API documentation and task lists
```

## Running the App
```bash
cd submissions/jhs/week4
conda activate cs146s
make run          # http://localhost:8000 (frontend) | /docs (Swagger)
make test         # pytest with PYTHONPATH=.
make format       # black + ruff --fix
make lint         # ruff check
make seed         # seed database if empty
```

## Code Style Rules
- **Line length:** 100 characters max
- **Formatter:** black (enforced via pre-commit)
- **Linter:** ruff with rules E, F, I, UP, B
- **Python:** 3.12, use modern type hints (list[X] not List[X])
- Always run `make format` before committing

## Architecture Patterns
- **Dependency injection:** Use `Depends(get_db)` for database sessions in all router endpoints
- **Pydantic v2:** Use `model_validate()` for ORM→schema conversion, `from_attributes = True` in Config
- **HTTP status codes:** 201 for creation, 404 for not found, 400 for validation errors
- **PATCH for partial updates**, PUT for full updates
- **Test isolation:** Each test gets a fresh temporary SQLite database (see conftest.py)

## Workflow: Adding a New Endpoint
1. Write a failing test in `backend/tests/test_<resource>.py`
2. Add Pydantic schema(s) to `backend/app/schemas.py`
3. Add model changes to `backend/app/models.py` (if needed)
4. Implement the endpoint in `backend/app/routers/<resource>.py`
5. Run `make test` to verify
6. Run `make format` to auto-fix style
7. Update frontend in `frontend/app.js` and `frontend/index.html` if UI changes needed
8. Run `/project:docs-sync` to update API documentation

## Workflow: Fixing a Bug
1. Reproduce with a failing test
2. Fix the code
3. Run `make test` to verify the fix
4. Run `make format` && `make lint`

## Safety Guardrails
- NEVER delete `data/app.db` without user confirmation
- NEVER run `DROP TABLE` commands
- Always use parameterized queries (SQLAlchemy handles this)
- Run tests before committing any changes
- Keep `docs/API.md` in sync after endpoint changes
