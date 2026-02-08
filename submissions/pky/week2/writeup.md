# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: Claude Code (Anthropic), Google Gemini API documentation

This assignment took me about **TODO** hours to do.


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Analyze the existing extract_action_items() function in week2/app/services/extract.py.
Implement an LLM-powered alternative called extract_action_items_llm() that uses the
Google Gemini API (google-genai) to perform action item extraction. The function should:
1. Accept a text string and return a list of action item strings
2. Use structured output (response_mime_type="application/json") to get a JSON array
3. Use the gemini-2.0-flash model with low temperature (0.2) for deterministic results
4. Include a system instruction telling the model to extract action items as a JSON array
5. Handle edge cases: empty input returns [], malformed JSON falls back to []
6. Follow the same function signature pattern as extract_action_items()
```

Generated Code Snippets:
```
week2/app/services/extract.py:3       - Added `import json`
week2/app/services/extract.py:72-102  - New function `extract_action_items_llm()`
  - Lines 78-79: Empty input guard
  - Lines 81-96: Gemini API call with structured output config
  - Lines 97-100: JSON parsing and type validation
  - Lines 101-102: Exception handling fallback
```

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for extract_action_items_llm() in week2/tests/test_extract.py.
Cover the following cases:
1. Bullet list input - mock Gemini to return JSON array, verify correct extraction
2. Keyword-prefixed lines (TODO:, Action:) - mock Gemini, verify extraction
3. Empty string input - should return [] without calling the API
4. Whitespace-only input - should return [] without calling the API
5. Malformed JSON response from LLM - should gracefully return []
6. Non-array JSON response (e.g. object) - should gracefully return []
7. API exception/error - should gracefully return []

Use unittest.mock.patch to mock the Gemini client at "week2.app.services.extract.client"
so tests run without an actual API key. Use MagicMock for response objects.
```

Generated Code Snippets:
```
week2/tests/test_extract.py:1-7     - Updated imports (added json, MagicMock, patch, extract_action_items_llm)
week2/tests/test_extract.py:31-40   - test_llm_extract_bullet_list() - mocked bullet list extraction
week2/tests/test_extract.py:43-53   - test_llm_extract_keyword_prefixed() - mocked keyword extraction
week2/tests/test_extract.py:56-59   - test_llm_extract_empty_input() - empty string guard
week2/tests/test_extract.py:62-65   - test_llm_extract_whitespace_only() - whitespace guard
week2/tests/test_extract.py:68-76   - test_llm_extract_malformed_json() - invalid JSON fallback
week2/tests/test_extract.py:79-87   - test_llm_extract_non_array_json() - object instead of array
week2/tests/test_extract.py:90-96   - test_llm_extract_api_error() - exception handling
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor the week2 backend for clarity, focusing on:
1. API contracts/schemas: Create week2/app/schemas.py with Pydantic v2 BaseModel classes
   for all request/response types (NoteCreate, NoteRead, ExtractRequest, ExtractResponse,
   ActionItemRead, MarkDoneRequest, MarkDoneResponse). Replace all Dict[str, Any] usage
   in routers with these typed schemas.
2. Database layer: Keep raw sqlite3 (no ORM migration), add error handling.
3. App lifecycle: Move init_db() from module-level execution to a FastAPI lifespan
   context manager for proper startup/shutdown handling.
4. Error handling: Add try/except around extraction calls in routers, use logging
   for error tracking, return proper HTTP status codes (201 for creation, 500 for errors).
5. Response models: Add response_model= to all router decorators for OpenAPI docs.
```

Generated/Modified Code Snippets:
```
week2/app/schemas.py (NEW FILE)
  Lines 1-43  - Complete Pydantic v2 schema definitions:
    - NoteCreate (line 7), NoteRead (line 11), ActionItemRead (line 18)
    - ExtractRequest (line 26), ExtractResponse (line 31)
    - MarkDoneRequest (line 37), MarkDoneResponse (line 41)

week2/app/main.py
  Lines 3,14-18  - Added asynccontextmanager import and lifespan() handler
  Line 21        - Added lifespan= parameter to FastAPI()
  Removed        - Module-level init_db() call, unused imports (Any, Dict, Optional, HTTPException)

week2/app/routers/notes.py
  Line 6         - Import NoteCreate, NoteRead from schemas
  Lines 12-19    - create_note() uses NoteCreate input, NoteRead response, status_code=201
  Lines 22-27    - get_single_note() uses NoteRead response_model

week2/app/routers/action_items.py
  Lines 3,17     - Added logging import and logger instance
  Lines 8-14     - Import all Pydantic schemas instead of Dict[str, Any]
  Lines 22-42    - extract() uses ExtractRequest/ExtractResponse, try/except error handling
  Lines 45-56    - list_all() uses list[ActionItemRead] response_model
  Lines 59-62    - mark_done() uses MarkDoneRequest/MarkDoneResponse
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
Using agentic mode, make the following changes:

1. Add a new LLM extraction endpoint: POST /action-items/extract-llm in the
   action_items router. It should mirror the existing /extract endpoint but call
   extract_action_items_llm() instead. Import it from services.extract.

2. Add a "List Notes" endpoint: GET /notes in the notes router that calls the
   existing db.list_notes() function and returns a list of NoteRead objects.

3. Update the frontend (week2/frontend/index.html) to add:
   - An "Extract LLM" button that calls POST /action-items/extract-llm
   - A "List Notes" button that calls GET /notes and displays results
   - Refactor the JS to share extraction logic via a helper function
   - Add a collapsible notes section to display fetched notes
```

Generated Code Snippets:
```
week2/app/routers/action_items.py
  Line 15        - Added extract_action_items_llm to import
  Lines 45-65    - New extract_llm() endpoint (POST /action-items/extract-llm)

week2/app/routers/notes.py
  Lines 22-28    - New list_notes() endpoint (GET /notes)

week2/frontend/index.html
  Lines 16-18    - Added CSS for .notes-section and .note-card
  Line 30        - Added "Extract LLM" button
  Line 31        - Added "List Notes" button
  Lines 36-39    - Added notes-section div (hidden by default)
  Lines 46-64    - Extracted renderItems() helper function
  Lines 66-84    - Extracted doExtract() helper function
  Lines 86-90    - Event listeners for both Extract and Extract LLM buttons
  Lines 92-113   - List Notes click handler with fetch and display logic
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Analyze the week2 codebase and generate a well-structured README.md that includes:
1. A brief overview of the project (Action Item Extractor - FastAPI + SQLite app
   that converts notes to action items via heuristic and LLM extraction)
2. How to set up and run the project (conda env, poetry install, .env config, uvicorn)
3. API endpoints and functionality (all 8 endpoints with methods, paths, descriptions,
   request/response schemas)
4. Instructions for running the test suite (pytest command, test coverage description)
Also include: project structure tree, tech stack, database schema, example curl commands.
```

Generated Code Snippets:
```
week2/README.md (NEW FILE)
  Full README documentation including:
  - Project overview and description
  - Setup and installation instructions
  - Running the application
  - Complete API endpoint documentation with request/response examples
  - Testing instructions
  - Project structure tree
  - Database schema
  - Error handling documentation
  - Example curl commands
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
