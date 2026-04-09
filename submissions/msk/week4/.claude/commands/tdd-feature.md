# TDD Feature Implementation

Implement the following feature using strict test-driven development:

**Feature request**: $ARGUMENTS

## Workflow

Follow these steps in exact order. Do not skip any step.

### Step 1: Analyze the feature
- Read the relevant source files to understand what exists
- Identify which files need to be created or modified
- Identify which test files need to be created or modified
- List your plan before writing any code

### Step 2: Write failing tests (RED phase)
- Create or update test file(s) in `backend/tests/`
- Write tests that describe the expected behavior of the feature
- Include both happy-path tests and edge-case tests (invalid input, not-found, etc.)
- Run `make test` from the `week4/` directory to confirm the new tests FAIL
- If tests pass without implementation, the tests are not testing new behavior -- revise them

### Step 3: Implement the feature (GREEN phase)
- Make the minimal code changes needed to pass the tests
- Update schemas in `backend/app/schemas.py` if needed
- Update models in `backend/app/models.py` if needed
- Update or create router endpoints in `backend/app/routers/`
- Update services in `backend/app/services/` if needed
- Run `make test` from the `week4/` directory to confirm ALL tests pass (new and existing)

### Step 4: Refactor (IMPROVE phase)
- Review the implementation for clarity and duplication
- Ensure no unnecessary code was added
- Verify naming is consistent with existing conventions

### Step 5: Format and lint
- Run `make format` from the `week4/` directory
- Run `make lint` from the `week4/` directory
- Fix any issues that arise

### Step 6: Update frontend (if applicable)
- If the feature involves new or changed endpoints that the UI should use, update `frontend/app.js` and `frontend/index.html`
- Keep frontend changes minimal and consistent with existing patterns

### Step 7: Summary
Provide a summary including:
- Files created or modified
- Tests added (list each test function name)
- Endpoints added or changed (method, path, status codes)
- Any remaining TODOs or follow-up items
