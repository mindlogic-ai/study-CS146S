---
allowed-tools: Bash, Read, Edit, Grep, Glob
description: Run tests, auto-fix failures, format/lint, and re-test
argument-hint: [optional test pattern, e.g. test_notes]
---

# Test → Fix → Retest Automation

Run the project test suite, and if any tests fail, automatically analyze the errors, fix the implementation code, apply formatting/linting, and re-run tests until they pass.

## Step 1: Run Tests

Run the test suite from the `submissions/mjk/week4/` directory. If `$ARGUMENTS` is provided, use it as a test filter pattern.

```bash
# If $ARGUMENTS is provided:
cd submissions/mjk/week4 && PYTHONPATH=. pytest -q backend/tests -k "$ARGUMENTS" --tb=short 2>&1

# Otherwise run all tests:
cd submissions/mjk/week4 && make test 2>&1
```

Capture the full output including any tracebacks.

## Step 2: Analyze Failures

If all tests pass, report success and stop.

If any tests fail:
1. Read the failing test file(s) to understand what behavior is expected
2. Read the corresponding implementation file(s) (routers, services, models, schemas)
3. Identify the root cause — do NOT guess, trace the actual code path

Key locations:
- Tests: `backend/tests/test_notes.py`, `backend/tests/test_action_items.py`, `backend/tests/test_extract.py`
- Routers: `backend/app/routers/notes.py`, `backend/app/routers/action_items.py`
- Services: `backend/app/services/extract.py`
- Schemas: `backend/app/schemas.py`
- Models: `backend/app/models.py`

## Step 3: Fix the Implementation

Apply fixes to the **implementation code only** (never modify test files).
- Follow existing code patterns (dependency injection, Pydantic validation, SQLAlchemy 2.0 style)
- Keep changes minimal and focused on passing the failing tests
- If a new endpoint is needed, add schema → router → wire up in main.py

## Step 4: Format & Lint

```bash
cd submissions/mjk/week4 && make format 2>&1
cd submissions/mjk/week4 && make lint 2>&1
```

Fix any lint errors that arise.

## Step 5: Re-run Tests

```bash
cd submissions/mjk/week4 && make test 2>&1
```

If tests still fail, repeat from Step 2 (max 3 iterations).

## Step 6: Report

Provide a summary:
- **Original failures**: list of failed tests and errors
- **Files modified**: list of changed files
- **Fixes applied**: brief description of each fix
- **Final result**: all tests pass / remaining failures
- **Rollback**: `git restore submissions/mjk/week4/backend/app/` to undo all changes

## Safety Rules

- NEVER modify test files — fix the implementation to match test expectations
- NEVER delete or recreate the database
- Keep all changes within `backend/app/`
- Maximum 3 fix-retest iterations to avoid infinite loops
