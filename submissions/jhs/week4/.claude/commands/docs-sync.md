# Docs Sync — API Documentation Generator

Synchronize API documentation with the actual OpenAPI spec to prevent docs drift.

## Instructions

1. **Read the current OpenAPI spec** by examining the FastAPI app's registered routes:
   - Read `backend/app/main.py` to find all included routers
   - Read each router file in `backend/app/routers/` to catalog every endpoint
   - For each endpoint, extract: method, path, request body schema, response model, status codes, and description

2. **Read the current docs** (if they exist):
   - Check if `docs/API.md` exists
   - If it exists, parse its contents to identify documented endpoints

3. **Generate/update `docs/API.md`** with the following structure:
   ```markdown
   # API Reference

   Auto-generated from source. Last synced: {current date}

   ## Endpoints

   ### Notes
   | Method | Path | Description | Request Body | Response | Status |

   ### Action Items
   | Method | Path | Description | Request Body | Response | Status |

   ## Schemas
   (List Pydantic schemas with their fields and types)
   ```

4. **Report drift** — compare old vs new docs:
   - List any **new endpoints** not previously documented
   - List any **removed endpoints** that were in old docs but no longer exist
   - List any **changed endpoints** (modified parameters, response models, etc.)
   - Present as a diff-like summary

5. **Write the updated `docs/API.md`** file.

## Inputs
- `$ARGUMENTS`: Optional — pass `--check-only` to report drift without writing changes.

## Safety
- Only modifies `docs/API.md` — never touches source code or tests
- Rollback: `git checkout docs/API.md` to restore previous version
- Idempotent: running multiple times produces the same output
