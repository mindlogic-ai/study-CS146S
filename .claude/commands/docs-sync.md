# Docs Sync — Generate API Documentation

Synchronize `week4/docs/API.md` with the actual API endpoints by reading the OpenAPI schema from the FastAPI app.

## Steps

1. **Read existing docs**: If `week4/docs/API.md` exists, read it and note the current documented endpoints for later comparison.

2. **Extract OpenAPI schema**: Run the following command to get the current API schema:
   ```bash
   cd week4 && PYTHONPATH=. python -c "from backend.app.main import app; import json; print(json.dumps(app.openapi(), indent=2))"
   ```

3. **Generate API.md**: Create or overwrite `week4/docs/API.md` with well-formatted documentation based on the OpenAPI schema. Include for each endpoint:
   - HTTP method and path
   - Description/summary
   - Request body schema (if any) with field types and constraints
   - Response schema with field types
   - Status codes (success and error)
   - Example request/response where helpful

4. **Detect drift**: Compare the newly generated documentation against the previous version (from step 1). Report:
   - **Added endpoints**: New routes not previously documented
   - **Removed endpoints**: Routes that were documented but no longer exist
   - **Changed endpoints**: Routes with modified schemas or parameters

5. **Summary**: Output a table of all documented endpoints and any drift detected.

## Output Format for API.md
```
# API Documentation

## Notes

### GET /notes/
...

### POST /notes/
...

## Action Items

### GET /action-items/
...
```

## Requirements
- Must run from the `week4/` directory (PYTHONPATH=. is required)
- Generated docs must accurately reflect the current API state
- Use clear markdown formatting with code blocks for schemas
