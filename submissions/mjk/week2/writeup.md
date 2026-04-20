# Week 2 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.

## YOUR RESPONSES

For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature

Prompt:

```
과제 요구사항:

### TODO 1: Scaffold a New Feature

Analyze the existing `extract_action_items()` function in `week2/app/services/extract.py`, which currently extracts action items using predefined heuristics.

Your task is to implement an **LLM-powered** alternative, `extract_action_items_llm()`, that utilizes Ollama to perform action item extraction via a large language model.

Some  tips:
- To produce structured outputs (i.e. JSON array of strings), refer to this documentation: https://ollama.com/blog/structured-outputs
- To browse available Ollama models, refer to this documentation: https://ollama.com/library. Note that larger models will be more resource-intensive, so start small. To pull and run a model: `ollama run {MODEL_NAME}`

나는 ollama 말고 gemini api로 해줘
```

Generated Code Snippets:

```
submissions/mjk/week2/app/services/extract.py: lines 3, 6, 72-87
- Added `import json` (line 3)
- Removed unused `Any` from typing imports (line 6)
- Added `extract_action_items_llm()` function (lines 72-87) that uses Gemini 2.0 Flash with structured output (response_mime_type="application/json", response_schema=list[str]) to extract action items from text
```

### Exercise 2: Add Unit Tests

Prompt:

```
과제 요구사항:
### TODO 2: Add Unit Tests

Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.
```

Generated Code Snippets:

```
submissions/mjk/week2/tests/test_extract.py: lines 1-2, 4, 28-95
- Added `import json`, `from unittest.mock import MagicMock, patch` (lines 1-2)
- Added import of `extract_action_items_llm` (line 4)
- Added `_mock_gemini_response()` helper (lines 28-31)
- Added `test_llm_extract_bullet_list` (lines 34-47)
- Added `test_llm_extract_keyword_prefixed` (lines 50-63)
- Added `test_llm_extract_empty_input` (lines 66-70)
- Added `test_llm_extract_no_action_items` (lines 73-78)
- Added `test_llm_extract_mixed_content` (lines 81-95)
```

### Exercise 3: Refactor Existing Code for Clarity

Prompt:

```
과제 요구사항:

Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling.
```

Generated/Modified Code Snippets:

```
submissions/mjk/week2/app/schemas.py (NEW): lines 1-55
- Created Pydantic v2 schemas: NoteCreate, NoteResponse, ExtractRequest, ActionItemOut, ExtractResponse, ActionItemResponse, MarkDoneRequest, MarkDoneResponse

submissions/mjk/week2/app/db.py: lines 4, 6, 13-27, 55, 58-62, 65-69, 72-76, 79, 82-92, 95-106, 109-114, 117-124
- Replaced per-function get_connection() with @contextmanager _get_conn() that auto-commits/rollbacks/closes (lines 13-27)
- Enabled PRAGMA foreign_keys (line 19)
- Simplified all DB functions to use conn.execute() directly instead of cursor pattern
- Added get_action_item() lookup function (lines 109-114)
- Changed mark_action_item_done() to return rowcount for 404 detection (lines 117-124)

submissions/mjk/week2/app/main.py: lines 3-4, 14, 17-20, 23
- Replaced module-level init_db() with FastAPI lifespan async context manager (lines 17-20)
- Extracted FRONTEND_DIR constant (line 14)
- Removed unused imports (Dict, Optional, Any, HTTPException)

submissions/mjk/week2/app/routers/notes.py: lines 3, 5-6, 10-18, 20-25
- Replaced Dict[str, Any] with Pydantic NoteCreate/NoteResponse schemas
- Added status_code=201 for creation endpoint
- Added 500 error guard after insert

submissions/mjk/week2/app/routers/action_items.py: lines 3, 5, 7-15, 21-32, 35-48, 51-55
- Replaced Dict[str, Any] with Pydantic ExtractRequest/ExtractResponse/ActionItemResponse/MarkDoneRequest/MarkDoneResponse
- Added status_code=201 for extract endpoint
- Added 404 error handling in mark_done when action item not found
```

### Exercise 4: Use Agentic Mode to Automate a Small Task

Prompt:

```
과제 요구사항:

1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.
```

Generated Code Snippets:

```
submissions/mjk/week2/app/routers/action_items.py: lines 16, 35-46
- Added import of extract_action_items_llm (line 16)
- Added POST /action-items/extract-llm endpoint using extract_action_items_llm() (lines 35-46)

submissions/mjk/week2/app/routers/notes.py: lines 20-26
- Added GET /notes endpoint listing all notes (lines 20-26)

submissions/mjk/week2/frontend/index.html: lines 27-28, 32, 37, 39-72, 74-75, 77-96
- Added "Extract LLM" and "List Notes" buttons (lines 27-28)
- Added #notes-list container (line 32)
- Refactored extract logic into reusable doExtract(endpoint) function (lines 39-72)
- Wired Extract button to /action-items/extract, Extract LLM to /action-items/extract-llm (lines 74-75)
- Added List Notes click handler fetching GET /notes and rendering cards (lines 77-96)
```

### Exercise 5: Generate a README from the Codebase

Prompt:

```
과제 요구사항:

Use Cursor to analyze the current codebase and generate a well-structured `README.md` file. The README should include, at a minimum:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite

너는 claude code니까 커서보다 잘할 수 있어
```

Generated Code Snippets:

```
submissions/mjk/week2/README.md: lines 1-82
- Project overview and structure diagram (lines 1-25)
- Setup & installation instructions with uv (lines 27-46)
- API endpoints table for Notes and Action Items (lines 48-72)
- Example curl requests for heuristic and LLM extraction (lines 63-72)
- Test running instructions (lines 74-82)
```

## SUBMISSION INSTRUCTIONS

1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
