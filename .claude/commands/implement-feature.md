# Implement Feature (TDD Workflow)

Implement the following feature using Test-Driven Development:

**Feature:** $ARGUMENTS

## Steps

1. **Understand context**: Read the relevant source files in `week4/` to understand the current codebase state. Check `week4/backend/app/models.py`, `week4/backend/app/schemas.py`, and the relevant router in `week4/backend/app/routers/`.

2. **Write failing tests first (RED)**: Based on the feature description, write or update tests in `week4/backend/tests/`. Cover both happy path and error cases (e.g., 404 for missing resources, 422 for invalid input).

3. **Verify tests fail**: Run `cd week4 && make test` to confirm the new tests fail as expected. This validates the tests are actually testing something new.

4. **Implement the feature (GREEN)**: Make the minimal code changes needed to pass the tests. This may involve:
   - Adding/updating schemas in `week4/backend/app/schemas.py`
   - Adding/updating routes in `week4/backend/app/routers/`
   - Adding/updating services in `week4/backend/app/services/`
   - Updating frontend in `week4/frontend/app.js` if UI changes are needed

5. **Verify tests pass**: Run `cd week4 && make test` to confirm ALL tests pass (both new and existing).

6. **Format and lint**: Run `cd week4 && make format && make lint` to ensure code style compliance.

7. **Summary**: Report what files were changed, what tests were added, and what the user should manually verify.

## Guidelines
- Follow existing code patterns (see `week4/CLAUDE.md` for conventions)
- Use Pydantic v2 style (`model_validate`, `from_attributes = True`)
- Use `Depends(get_db)` for database sessions
- Return HTTP 201 for creation, 404 for not found, 422 for validation errors
- Keep changes minimal and focused on the described feature
