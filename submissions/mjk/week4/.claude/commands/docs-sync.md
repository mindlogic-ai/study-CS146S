---
allowed-tools: Bash, Read, Write, Glob
description: Sync docs/API.md from OpenAPI spec and show route deltas
---

# API Documentation Sync

Fetch the FastAPI OpenAPI spec and generate/update `docs/API.md` with current API routes, then show a diff summary of any changes.

## Step 1: Check Server Status

Check if the FastAPI server is running on localhost:8000:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/openapi.json 2>/dev/null || echo "NOT_RUNNING"
```

If the server is NOT running, start it in the background:

```bash
cd submissions/mjk/week4 && PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
sleep 2
```

## Step 2: Fetch OpenAPI Spec

```bash
curl -s http://localhost:8000/openapi.json
```

Parse the JSON response. Extract:
- All route paths and HTTP methods
- Request body schemas (if any)
- Response schemas
- Query parameters
- Path parameters
- Tags/grouping

## Step 3: Read Existing Docs

Read `submissions/mjk/week4/docs/API.md` if it exists. Extract the list of previously documented routes to compare later.

If the file doesn't exist, note that this is a first-time generation.

## Step 4: Generate API.md

Write `submissions/mjk/week4/docs/API.md` in this format:

```markdown
# API Documentation

> Auto-generated from OpenAPI spec via `/docs-sync`
> Last synced: {current date}

## Base URL
`http://localhost:8000`

## Endpoints

### Notes
#### GET /notes/
- Description: ...
- Response: `200` - `List[NoteRead]`
  - id: integer
  - title: string
  - content: string

#### POST /notes/
- Description: ...
- Request Body: `NoteCreate`
  - title: string (required)
  - content: string (required)
- Response: `201` - `NoteRead`

(... repeat for each endpoint ...)

### Action Items
(... same structure ...)

## Schemas
### NoteCreate
| Field | Type | Required |
|-------|------|----------|
| title | string | yes |
| content | string | yes |

(... repeat for each schema ...)
```

Organize endpoints by their tags (notes, action_items).

## Step 5: Show Diff Summary

Compare old routes (from Step 3) vs new routes (from Step 4):

- **Added**: routes that exist in OpenAPI but not in old docs
- **Removed**: routes that were in old docs but no longer in OpenAPI
- **Modified**: routes where schemas or parameters changed

Present the summary clearly:
```
Route Delta Summary:
  Added:    PUT /notes/{note_id}
  Added:    DELETE /notes/{note_id}
  Modified: GET /notes/ (added query params: skip, limit)
  Removed:  (none)
```

If this is the first generation, list all routes as "Added".

## Step 6: Final Report

- Confirm `docs/API.md` has been written/updated
- Show the route delta summary
- Note any discrepancies or TODOs (e.g., missing descriptions)

## Notes

- This command is idempotent — safe to run multiple times
- Only modifies `docs/API.md`, never touches source code
- Requires the server to be running (will auto-start if needed)
