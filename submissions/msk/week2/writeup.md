# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Minseo Kim \
SUNet ID: idk \
Citations: Claude Code (Claude Opus 4.6) used as AI coding assistant in place of Cursor.

This assignment took me about 0.5 hours to do.


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Implement extract_action_items_llm using gemini. Make sure to let llm output to be
structured in json format. Try simple prompt while using xml tags.
```
Additional guidance given during generation:
- Use multi-line string for prompt instead of string concatenation
- Give example of output format instead of explaining the format
- Use gemini-3-flash model

Generated Code Snippets:
```
week2/app/services/extract.py: lines 72-103
  - Added extract_action_items_llm() function
  - Uses f-string multi-line prompt with <task>, <notes>, and <output_format> XML tags
  - Gemini structured output via response_mime_type="application/json" and response_schema=list[str]
  - temperature=0.0 for deterministic results
  - Early return for empty/whitespace input
  - Post-processing strips whitespace and filters empty strings

week2/app/services/extract.py: line 3
  - Added `import json` to top-level imports
```

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for extract_action_items_llm().
- Cover multiple input types: bullet lists, keyword-prefixed lines, empty input
```
Additional guidance: keep tests simple, following the pattern of the existing `test_extract_bullets_and_checkboxes()` test (no mocking).

Generated Code Snippets:
```
week2/tests/test_extract.py: lines 3, 21-50
  - line 3: Updated import to include extract_action_items_llm
  - lines 21-32: test_llm_extract_bullet_list() - feeds bullet list input, asserts LLM
    returns items about database, API endpoint, and tests using loose keyword matching
  - lines 35-45: test_llm_extract_keyword_prefixed() - feeds todo:/action: prefixed lines
    mixed with narrative, checks it picks up action items and ignores comments
  - lines 48-50: test_llm_extract_empty_input() - verifies empty and whitespace-only
    input returns [] without calling the API
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor backend codes in week2/app/ for clarity.
Checklist:
- are API contracts/schemas well defined?
- database layer is properly cleaned up?
- app lifecycle / configuration
- error handling
```

Generated/Modified Code Snippets:
```
week2/app/schemas.py: lines 1-55 (NEW FILE)
  - Pydantic models for all API contracts:
    NoteCreate, NoteResponse, ExtractRequest, ExtractResponse,
    ActionItemBrief, ActionItemResponse, MarkDoneRequest, MarkDoneResponse
  - Field validation with min_length=1 on content and text fields

week2/app/main.py: lines 1-35 (REWRITTEN)
  - Replaced module-level init_db() call with async lifespan context manager
  - Extracted FRONTEND_DIR as module constant (was duplicated)
  - Removed unused imports (HTTPException, Dict, Any, db)

week2/app/db.py: lines 1-118 (REWRITTEN)
  - Removed redundant ensure_data_directory_exists() helper; directory creation
    now happens once in init_db()
  - Added PRAGMA foreign_keys = ON in get_connection() (SQLite doesn't enforce FKs by default)
  - Added get_action_item() lookup function (lines 101-108) to support 404 checks
  - Replaced Optional[X] with X | None for consistency

week2/app/routers/action_items.py: lines 1-58 (REWRITTEN)
  - Replaced Dict[str, Any] payloads with Pydantic schemas (ExtractRequest, MarkDoneRequest)
  - Added response_model declarations on all endpoints
  - mark_done now returns 404 if action item doesn't exist (lines 52-55)

week2/app/routers/notes.py: lines 1-37 (REWRITTEN)
  - Replaced Dict[str, Any] payloads with Pydantic schemas (NoteCreate, NoteResponse)
  - Added response_model declarations on all endpoints
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
Revise the code to properly use endpoint

1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include
   an "Extract LLM" button that, when clicked, triggers the extraction process via the
   new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a
   "List Notes" button that, when clicked, fetches and displays them.
```
Claude Code autonomously identified all files to modify, made changes across 3 files in a single pass, and refactored the frontend JS to share logic between the two extract buttons.

Generated Code Snippets:
```
week2/app/routers/action_items.py: lines 14, 36-50
  - line 14: Added extract_action_items_llm to import
  - lines 36-50: New POST /action-items/extract-llm endpoint using extract_action_items_llm()

week2/app/routers/notes.py: lines 23-29
  - New GET /notes endpoint returning list[NoteResponse] via db.list_notes()

week2/frontend/index.html: lines 16-18, 30-31, 34-35, 42-99
  - lines 16-18: Added CSS for .notes-list and .note-card
  - line 30: Added "Extract LLM" button
  - line 31: Added "List Notes" button
  - line 35: Added #notes-list container div
  - lines 42-76: Extracted shared handleExtract(endpoint) function to avoid
    duplicating fetch/render logic between Extract and Extract LLM buttons
  - lines 78-79: Wired both extract buttons to handleExtract with their respective endpoints
  - lines 81-99: Added List Notes click handler that fetches GET /notes and renders note cards
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Write well-structured README file for the week2 repository.
Content:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite
```
Claude Code read all backend files, schemas, pyproject.toml, and routers to generate an accurate README reflecting the current state of the codebase.

Generated Code Snippets:
```
week2/README.md: lines 1-107 (NEW FILE)
  - Project overview describing heuristic + LLM extraction
  - Project structure tree with one-line descriptions per module
  - Setup section: prerequisites (Python 3.10+, Poetry, Gemini API key),
    poetry install, .env configuration
  - Running the server: uvicorn command
  - API endpoints: tables for all 7 endpoints with example request/response JSON
  - Running tests: pytest command with note about API key requirement
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
