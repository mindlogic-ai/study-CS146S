# API Documentation Sync

Synchronize API documentation with the actual codebase. Generate or update `docs/API.md` to accurately reflect all registered endpoints.

## Workflow

### Step 1: Discover all routes
- Read `backend/app/main.py` to find all included routers
- Read each router file in `backend/app/routers/` to catalog every endpoint:
  - HTTP method (GET, POST, PUT, DELETE, PATCH)
  - Path (including path parameters)
  - Query parameters
  - Request body schema (reference the Pydantic model)
  - Response model and status code
  - Brief description from the function docstring or name

### Step 2: Read existing documentation
- Check if `docs/API.md` exists
- If it exists, parse its current contents to identify documented endpoints
- If it does not exist, note that this is a fresh creation

### Step 3: Read Pydantic schemas
- Read `backend/app/schemas.py` to document request/response shapes
- Include field names, types, and any validation constraints

### Step 4: Generate or update docs/API.md
Use this format for each endpoint group:

```
## Resource Name

### Endpoint description
- **Method**: GET/POST/PUT/DELETE
- **Path**: `/resource/`
- **Query params**: (if any)
- **Request body**: SchemaName -- `{ field: type, ... }`
- **Response**: `status_code` -- SchemaName
- **Description**: What the endpoint does.
```

Group endpoints by router/resource. Include a "Schemas" section at the bottom documenting each Pydantic model with its fields, types, and validation constraints.

### Step 5: Drift report
Compare the generated documentation against what was previously in `docs/API.md` (if anything). Report:
- **New endpoints**: routes in code but not previously documented
- **Removed endpoints**: routes previously documented but no longer in code
- **Changed endpoints**: routes where method, path, or schemas differ
- If no previous docs existed, report all endpoints as "New"

### Step 6: Verify
- Run `make test` to confirm no code was accidentally changed
- Print the drift report summary
