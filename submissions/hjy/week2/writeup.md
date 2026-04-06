# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Hyungjoon \
SUNet ID: hjy \
Citations: Claude Code (Claude Opus 4.6) for code generation and refactoring assistance

This assignment took me about 2 hours to do.


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Implement an LLM-powered extract_action_items_llm() function in week2/app/services/extract.py
that uses the existing Gemini API client to extract action items from text. Use structured JSON
output (response_mime_type="application/json") to return a list of strings. Handle empty input
by returning an empty list.
```

Generated Code Snippets:
```
- app/services/extract.py: lines 16-49 (EXTRACTION_PROMPT, extract_action_items_llm function)
```

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for extract_action_items_llm() in week2/tests/test_extract.py covering:
bullet list input, keyword-prefixed lines (todo:, action:, next:), empty input, and narrative
text with imperative sentences. Use pytest.mark.skipif to skip tests when GEMINI_API_KEY is not
set. Use flexible assertions since LLM may rephrase outputs.
```

Generated Code Snippets:
```
- tests/test_extract.py: lines 22-69 (TestExtractActionItemsLLM class with 4 test methods)
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor the week2 backend for clarity:
1. Add Pydantic v2 schemas for all request/response types (NoteCreate, NoteResponse,
   ExtractRequest, ExtractResponse, ActionItemResponse, MarkDoneRequest)
2. Replace Dict[str, Any] in routers with Pydantic models for type-safe validation
3. Use HTTP 201 status code for creation endpoints
4. Move init_db() into FastAPI lifespan context manager instead of module-level call
5. Add proper error handling for database operations
```

Generated/Modified Code Snippets:
```
- app/schemas.py: new file, lines 1-42 (all Pydantic schemas)
- app/routers/notes.py: lines 1-37 (refactored with Pydantic schemas, added response_model)
- app/routers/action_items.py: lines 1-59 (refactored with Pydantic schemas, status codes)
- app/main.py: lines 1-37 (lifespan context manager, FRONTEND_DIR constant)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
Add two new features:
1. A POST /action-items/extract-llm endpoint that uses extract_action_items_llm() for
   LLM-powered extraction. Add an "Extract LLM" button to the frontend that calls this endpoint.
2. A GET /notes endpoint that returns all saved notes. Add a "List Notes" button to the
   frontend that fetches and displays all notes in card format.
Refactor the frontend JS to share extraction logic between the two extract buttons.
```

Generated Code Snippets:
```
- app/routers/action_items.py: lines 32-43 (extract_llm endpoint)
- app/routers/notes.py: lines 14-20 (list_notes endpoint)
- frontend/index.html: lines 1-107 (Extract LLM button, List Notes button, shared JS helpers)
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Analyze the week2 codebase and generate a README.md that includes: project overview, setup
instructions (conda, poetry, .env), how to run the server, API endpoint table (all routes
with methods and descriptions), and how to run tests (heuristic-only and LLM tests separately).
```

Generated Code Snippets:
```
- README.md: new file (project overview, setup, API docs, test instructions, tech stack)
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
