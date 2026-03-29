# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **신재호 (Jaeho Shin)** \
SUNet ID: **jhs** \
Citations: **Claude Code (Claude Opus 4.6), Google Gemini API docs, Context7 docs**

This assignment took me about **2** hours to do.


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Implement an LLM-powered alternative extract_action_items_llm() in extract.py that uses the Google Gemini API (gemini-3-flash-preview) to extract action items from free-form text. Use structured output with a Pydantic model so Gemini returns a JSON array of action-item strings. Return an empty list for empty input without calling the API.
```

Generated Code Snippets:
```
- submissions/jhs/week2/app/services/extract.py: lines 93-120
  - Added Pydantic `ActionItems` model and `extract_action_items_llm()` function
  - Uses Gemini structured output (response_mime_type="application/json", response_schema=ActionItems)
  - Added `from pydantic import BaseModel` import at line 8
```

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for extract_action_items_llm() in test_extract.py covering: empty input, bullet lists, keyword-prefixed lines (todo:/action:), no action items in text, and mixed-format notes. Use unittest.mock to mock the Gemini API client so tests don't require a real API key.
```

Generated Code Snippets:
```
- submissions/jhs/week2/tests/test_extract.py: lines 27-98
  - _mock_gemini_response() helper function (lines 30-36)
  - TestExtractActionItemsLlm class with 5 test methods:
    - test_empty_input_returns_empty (lines 42-45)
    - test_bullet_list (lines 47-56)
    - test_keyword_prefixed_lines (lines 58-68)
    - test_no_action_items (lines 70-76)
    - test_mixed_format_notes (lines 78-98)
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor the backend code for clarity: add Pydantic schemas for all API request/response models, use FastAPI lifespan for DB initialization instead of module-level init_db() call, add response_model annotations to all router endpoints, replace Dict[str, Any] payloads with typed Pydantic models, and clean up path configuration.
```

Generated/Modified Code Snippets:
```
- submissions/jhs/week2/app/schemas.py (NEW FILE): lines 1-40
  - NoteCreateRequest, NoteResponse
  - ExtractRequest, ExtractResponse, ActionItemResponse
  - ActionItemDetail, MarkDoneRequest, MarkDoneResponse

- submissions/jhs/week2/app/main.py: lines 1-41 (fully refactored)
  - Added asynccontextmanager lifespan for DB init (lines 21-25)
  - Extracted BASE_DIR / FRONTEND_DIR constants (lines 16-17)
  - Removed unused imports

- submissions/jhs/week2/app/routers/notes.py: lines 1-35 (fully refactored)
  - Replaced Dict[str, Any] with NoteCreateRequest / NoteResponse schemas
  - Added response_model and status_code=201 to POST endpoint

- submissions/jhs/week2/app/routers/action_items.py: lines 1-75 (fully refactored)
  - Replaced Dict[str, Any] with typed Pydantic schemas
  - Added response_model annotations to all endpoints
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
1) Integrate the LLM-powered extraction as a new POST /action-items/extract-llm endpoint. Update the frontend to include an "Extract LLM" button that triggers extraction via the new endpoint.
2) Add a GET /notes endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that fetches and displays them.
```

Generated Code Snippets:
```
- submissions/jhs/week2/app/routers/action_items.py: lines 39-54
  - New extract_llm() endpoint at POST /action-items/extract-llm

- submissions/jhs/week2/app/routers/notes.py: lines 20-27
  - New list_notes() endpoint at GET /notes

- submissions/jhs/week2/frontend/index.html: lines 32-34
  - "Extract LLM" and "List Notes" buttons added to the button row
- submissions/jhs/week2/frontend/index.html: lines 46-111
  - Refactored JS: shared doExtract() helper, LLM click handler, List Notes click handler
  - Added .notes-list / .note-card CSS styles (lines 17-19)
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Analyze the current week2 codebase and generate a well-structured README.md that includes: project overview, project structure, setup instructions (conda, poetry, .env), how to run the server, all API endpoints with methods/paths/descriptions, example curl request, and instructions for running the test suite.
```

Generated Code Snippets:
```
- submissions/jhs/week2/README.md (NEW FILE): full file
  - Project overview, structure tree, setup guide, API endpoint table, example request, test instructions
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
