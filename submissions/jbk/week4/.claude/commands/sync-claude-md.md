---
disable-model-invocation: true
---

# CLAUDE.md Sync — Codebase Documentation Generator

Analyze the current codebase and generate/update the `CLAUDE.md` file to reflect the actual project state.

## Workflow

### Step 1: Analyze Project Structure
Read the directory structure to understand the codebase layout:
- List all Python files in `backend/app/` and `backend/tests/`
- List frontend files in `frontend/`
- Check for configuration files (`Makefile`, `pyproject.toml`, `.env.example`)
- Check for data files (`data/seed.sql`)

### Step 2: Extract API Endpoints
Read all router files in `backend/app/routers/` and extract:
- HTTP method (GET, POST, PUT, DELETE, PATCH)
- Path (e.g., `/notes/`, `/notes/{id}`)
- Function name
- Response model
- Status code (if non-default)

Format as a table:
```
| Method | Path | Description | Status |
|--------|------|-------------|--------|
```

### Step 3: Extract Code Style Configuration
Read `pyproject.toml` (if it exists at the project or repo root) and extract:
- Line length
- Formatter settings (black)
- Linter rules (ruff)
- Python version target

If no local `pyproject.toml` exists, check parent directories.

### Step 4: Extract Development Commands
Read `Makefile` and list all available targets with descriptions.

### Step 5: Check Test Coverage
Run:
```bash
PYTHONPATH=. pytest -q backend/tests/ 2>&1
```
Report the number of tests and pass/fail status.

### Step 6: Generate CLAUDE.md
Create or update `CLAUDE.md` in the current week directory with these sections:

```markdown
# CLAUDE.md — Week 4 Starter App

## Project Overview
[Brief description based on main.py app title and structure]

## Quick Commands
[From Makefile]

## Architecture
[Directory structure and key file descriptions]

## API Endpoints
[Table extracted from routers]

## Data Models
[From models.py — table name, columns, types]

## Schemas
[From schemas.py — request/response models]

## Code Style
[From pyproject.toml or defaults]

## Testing
[Test count, fixture setup, how to run]

## Development Workflow
[How to set up, run, test the project]
```

### Step 7: Report Changes
Output a summary of what was generated/updated:
- Sections written
- Number of endpoints documented
- Number of models documented
- Any discrepancies found (e.g., undocumented endpoints)
