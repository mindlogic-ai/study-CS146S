# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: JaewonKim \
SUNet ID: J \
Citations: Claude Code (Anthropic) for code generation and refactoring across all exercises. Google Gemini 2.0 Flash API for LLM-powered action item extraction. FastAPI and Pydantic official documentation for schema design patterns.

This assignment took me about 0.4 hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Implement an LLM-powered alternative extract_action_items_llm() in week2/app/services/extract.py that uses the Gemini API to extract action items from free-form text. Use structured output (response_mime_type="application/json" with response_schema=list[str]) to guarantee a JSON array of strings. Include error handling and logging.
```

Generated Code Snippets:
```
week2/app/services/extract.py (lines 72–105): Added extract_action_items_llm() function that sends text to Gemini 2.0 Flash with a structured output schema, parses the JSON response, and returns a list of action item strings. Includes try/except with logging for debugging.
```

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for extract_action_items_llm() in week2/tests/test_extract.py covering multiple input types: bullet lists, keyword-prefixed lines (todo:, action:), empty/whitespace input, text with no action items, and mixed format input. Mock the Gemini API client so tests run without an API key.
```

Generated Code Snippets:
```
week2/tests/test_extract.py (lines 28–98): Added 5 test functions using unittest.mock.patch to mock the Gemini client:
- test_llm_extract_bullet_list (lines 38–47)
- test_llm_extract_keyword_prefixed (lines 50–58)
- test_llm_extract_empty_input (lines 61–71)
- test_llm_extract_no_action_items (lines 74–81)
- test_llm_extract_mixed_format (lines 84–98)
Also added FakeResponse helper class (lines 31–35).
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor the backend code for clarity: (1) Add Pydantic v2 schemas for all request/response types instead of Dict[str, Any], (2) Update routers to use typed schemas with proper response_model and status codes, (3) Refactor main.py to use FastAPI lifespan instead of calling init_db() at module level, (4) Clean up unused imports.
```

Generated/Modified Code Snippets:
```
week2/app/schemas.py (new file, lines 1–48): Created Pydantic v2 models — NoteCreate, ExtractRequest, MarkDoneRequest (requests) and NoteResponse, ActionItemResponse, ExtractResponse, ActionItemDetail, MarkDoneResponse (responses).

week2/app/main.py (lines 1–36): Replaced module-level init_db() call with async lifespan context manager. Extracted FRONTEND_DIR as a module constant.

week2/app/routers/notes.py (lines 1–32): Replaced Dict[str, Any] with Pydantic schemas (NoteCreate, NoteResponse). Added status_code=HTTP_201_CREATED for POST endpoint.

week2/app/routers/action_items.py (lines 1–72): Replaced Dict[str, Any] with Pydantic schemas (ExtractRequest, ExtractResponse, MarkDoneRequest, MarkDoneResponse, ActionItemDetail). Removed unused HTTPException and status imports.

week2/app/services/extract.py (line 6): Removed unused Any import.
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
(1) Add a new POST /action-items/extract-llm endpoint that uses extract_action_items_llm() for LLM-powered extraction. (2) Add a GET /notes endpoint to retrieve all saved notes. (3) Update the frontend HTML to include an "Extract LLM" button that calls the new LLM endpoint and a "List Notes" button that fetches and displays all saved notes.
```

Generated Code Snippets:
```
week2/app/routers/action_items.py (lines 38–51): Added POST /action-items/extract-llm endpoint calling extract_action_items_llm().

week2/app/routers/notes.py (lines 20–24): Added GET /notes endpoint returning all saved notes.

week2/frontend/index.html (lines 32–34): Added "Extract LLM" and "List Notes" buttons.
week2/frontend/index.html (lines 47–110): Added shared handleExtract() function for both extraction modes, LLM button click handler, and List Notes click handler that fetches and renders note cards.
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Analyze the current codebase and generate a README.md for the week2 project. Include: project overview, setup/installation instructions, how to run the server, all API endpoints with methods and descriptions, how to run the test suite, and the project directory structure.
```

Generated Code Snippets:
```
week2/README.md (new file): Complete README with project overview, setup instructions (conda + poetry), server run command, API endpoints table (7 endpoints across notes and action-items), test command, and project directory tree.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 