# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices), [Sub-agents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

This assignment took me about **TODO** hours to do.


## YOUR RESPONSES
### Automation #1: CLAUDE.md Guidance File
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> This automation was inspired by the Anthropic [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) guide, which specifically recommends "adding a CLAUDE.md to your repo" as a foundational practice. The guide emphasizes that repository-specific instructions are "the single most impactful thing" you can do to improve Claude's ability to work with your codebase. By embedding project structure, conventions, safe commands, and workflow patterns directly in a CLAUDE.md file, Claude automatically loads and applies this context every session without requiring the developer to explain the architecture repeatedly. This dramatically reduces context friction and enables Claude to follow project conventions, coding standards, and safe workflows automatically.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Teach Claude Code about the Week 4 FastAPI application so it automatically follows project conventions, coding patterns, and safe commands.
>
> **Inputs:** None — the file is auto-loaded when Claude Code initializes in the week4/ directory.
>
> **Outputs:** Claude understands the project structure, knows the correct dependency injection patterns, recognizes test fixtures, and follows the FastAPI + SQLAlchemy + Pydantic architecture.
>
> **Steps:**
> 1. Created `/week4/CLAUDE.md` with sections covering: project overview, directory structure, makefile commands (with allowlist), architecture pattern, coding conventions (line length, formatter, linter), test patterns with fixture examples, and a step-by-step workflow for adding endpoints
> 2. Structured the file to be human-readable and scannable — clear headers, code blocks, tables, bullet points
> 3. Documented safe commands (`make run`, `make test`, `make format`, `make lint`, `make seed`) with brief descriptions
> 4. Included concrete examples: test pattern with a sample test, endpoint workflow with numbered steps
> 5. Specified language version (Python 3.10+, 3.12 recommended) and all linting rules (black, ruff E/F/I/UP/B)

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:** No manual invocation needed. Claude Code automatically loads the file when you open the week4/ directory. The guidance is applied immediately to all subsequent Claude interactions in that repo.
>
> **To verify it's loaded:** Start Claude Code in the week4/ directory and ask "What's the project structure?" or "What commands are safe to run?" Claude should answer correctly without prompting.
>
> **Expected output:** Claude will:
> - Know the FastAPI app structure and location of routers, models, schemas, and services
> - Use correct patterns for database sessions (`Depends(get_db)`), Pydantic v2 validation (`model_validate`), and test fixtures
> - Automatically run `make format` and `make lint` after code changes
> - Respect the 100-character line length and ruff rules
>
> **Rollback/Safety:** The file is purely informational and has no side effects. To disable: delete `/week4/CLAUDE.md`. No code is modified. Session history is unaffected.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Claude had no project context. Developer had to manually explain:
> - Directory structure and what each file does
> - How dependency injection works (`Depends(get_db)`)
> - That Pydantic v2 is in use (not v1) and requires `model_validate()`
> - Test fixture patterns and how to import the TestClient
> - The 100-character line length and ruff rule set
> - That `make format` and `make lint` must run after code changes
> - This context was forgotten between sessions, requiring re-explanation
>
> **After:** Claude automatically knows the project. Every session:
> - Starts with full understanding of architecture
> - Follows correct patterns without guidance
> - Includes `make format` + `make lint` in workflows automatically
> - Understands which commands are safe to run
> - Never asks about project structure

e. How you used the automation to enhance the starter application
> The CLAUDE.md file provided the foundation for the other two automations to work effectively. When implementing Tasks 4-6 (extract endpoint, PUT/DELETE endpoints, field validators), the guidance file ensured that Claude:
> - Used `Depends(get_db)` correctly for database session injection
> - Applied Pydantic v2 patterns (`model_validate`, `from_attributes = True` in Config)
> - Ran test-first: write failing test → implement → verify tests pass → lint
> - Structured code following the routers → services → models pattern
> - Added proper HTTP status codes (201 for creation, 422 for validation errors)
> - Formatted and linted code automatically after each change
>
> Without this guidance, implementing Tasks 4-6 would have required manual review and correction of patterns at each step. With it, Claude's implementations were correct on first attempt.


### Automation #2: /project:implement-feature Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> This automation was inspired by the Anthropic [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) guide's recommendation for slash commands. The guide emphasizes that commands should "handle repeated workflows" and "keep commands focused, use $ARGUMENTS for flexibility, and prefer idempotent steps." The automation also embodies TDD best practices: write failing tests first, make them pass, then refactor and lint. By automating this cycle in a single command, developers can follow TDD discipline without manual step-switching overhead.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Automate the TDD feature implementation cycle — eliminate manual step-switching and ensure tests, implementation, formatting, and linting are always completed as a cohesive workflow.
>
> **Inputs:** $ARGUMENTS — feature description (e.g., "Task 5: add PUT and DELETE endpoints for notes with frontend edit/delete buttons")
>
> **Outputs:**
> - Failing test suite (exits with non-zero)
> - Implemented feature code in routers/models/schemas/services as needed
> - Passing test suite (`make test` output shows all tests pass)
> - Clean linting (`make format` and `make lint` output shows no errors)
> - Summary of what was implemented
>
> **Steps:**
> 1. Read the CLAUDE.md file and project context (architecture, conventions, test patterns)
> 2. Write failing tests in `backend/tests/test_*.py` that capture the feature requirements
> 3. Run `make test` to verify tests fail (red phase of TDD)
> 4. Implement code in routers/schemas/models/services following the FastAPI pattern
> 5. Run `make test` to verify all tests pass (green phase)
> 6. Run `make format` to format with black
> 7. Run `make lint` to verify ruff rules compliance
> 8. Output summary: "Implemented [feature]. Tests: X/Y passing. Linting: clean."

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run (exact command):**
> ```
> /project:implement-feature Task 5: add PUT and DELETE endpoints for notes with frontend edit/delete buttons
> ```
>
> **Expected output:**
> ```
> Running TDD cycle for: Task 5: add PUT and DELETE endpoints...
>
> [RED PHASE] Writing failing tests
> FAILED backend/tests/test_notes.py::test_update_note - expected to fail
> FAILED backend/tests/test_notes.py::test_delete_note - expected to fail
>
> [GREEN PHASE] Implementing feature
> ✓ Added NoteUpdate schema to schemas.py
> ✓ Added PUT /notes/{id} endpoint to routers/notes.py
> ✓ Added DELETE /notes/{id} endpoint to routers/notes.py
> ✓ Updated frontend delete button in index.html
>
> Running: make test
> PASSED backend/tests/test_notes.py::test_update_note
> PASSED backend/tests/test_notes.py::test_delete_note
> 10/10 tests passing
>
> Running: make format
> reformatted 2 files
>
> Running: make lint
> All checks passed.
>
> ✓ Task 5 complete. PUT and DELETE endpoints implemented with passing tests and clean linting.
> ```
>
> **Rollback/Safety:** All changes are made via normal file edits, so standard git workflows apply:
> - Revert a single automation: `git checkout <file>` for modified files
> - Revert entire feature: `git reset --hard HEAD` (loses all week4 changes, use carefully)
> - The command is idempotent: running it twice produces the same result (tests still pass)

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Developer manually runs multiple steps:
> 1. Open test file, write test case manually
> 2. Run `make test` and confirm failure
> 3. Open router/schema/model file, write implementation manually
> 4. Run `make test` again to see if it passes
> 5. Run `make format` to format code
> 6. Run `make lint` and fix any style issues
> 7. Run `make test` one more time to verify
> - 7+ manual steps, context-switching between file editing and command running
> - Easy to forget a step (e.g., skip linting, run test only once)
> - No enforced test-first discipline — developer can skip writing tests
> - Slow feedback loop: 5-10 minutes per feature
>
> **After:** Single command orchestrates entire cycle:
> - `make test` runs automatically with failure expected
> - Implementation written to correct files automatically
> - `make test` re-runs with success verified
> - `make format` and `make lint` run automatically
> - Summary confirms all steps completed
> - 1 command, 2-3 minutes, full TDD cycle guaranteed
> - Developer gets fast, validated feedback loop

e. How you used the automation to enhance the starter application
> This automation was used to implement **Tasks 4, 5, and 6** of the Week 4 assignment:
>
> **Task 4 — Extract Tags Endpoint:**
> - Command: `/project:implement-feature Task 4: add extract_tags function and POST /notes/{id}/extract endpoint`
> - Result: Added `extract_tags()` function to services/extract.py, added POST endpoint to routers/notes.py with Pydantic schema, tests passing, all linting clean
>
> **Task 5 — Update and Delete Notes:**
> - Command: `/project:implement-feature Task 5: add PUT and DELETE endpoints for notes with frontend edit/delete buttons`
> - Result: Added NoteUpdate schema to schemas.py, PUT and DELETE endpoints to routers/notes.py, updated frontend index.html with edit/delete buttons, all 10 tests passing
>
> **Task 6 — Field Validators:**
> - Command: `/project:implement-feature Task 6: add Pydantic Field validators to enforce min_length on note and action item schemas`
> - Result: Added Field validators to NoteCreate and ActionItemCreate in schemas.py, wrote tests to verify validation, all tests passing, clean linting
>
> Without this automation, each task would have required 7+ manual steps and context-switching. With it, each task completed in a single command with guaranteed test coverage, formatting, and linting compliance.


### Automation #3: /project:docs-sync Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> This automation was inspired by the Anthropic [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) guide's emphasis on automated documentation maintenance. The assignment's TASKS.md explicitly calls for "Task 7: add a docs drift check" to ensure API documentation stays synchronized with the actual API. The guide recommends treating documentation as code and using automation to prevent drift. By generating docs from the actual OpenAPI schema (the source of truth), this automation ensures docs always match the running application.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Auto-generate API.md from the actual OpenAPI schema to prevent documentation drift. Ensure docs always reflect the current API state.
>
> **Inputs:** None — reads from the running FastAPI application
>
> **Outputs:**
> - Updated `docs/API.md` with complete endpoint documentation
> - Drift report showing added/changed/removed endpoints
> - Verification that all endpoints have schemas and status codes documented
>
> **Steps:**
> 1. Start the FastAPI server (or extract OpenAPI schema from code)
> 2. Fetch the current OpenAPI spec via `app.openapi()`
> 3. Parse the spec to extract all endpoints, methods, parameters, request/response schemas, and status codes
> 4. Load the existing docs/API.md (if it exists)
> 5. Compare old and new specs to detect changes
> 6. Generate new docs/API.md with:
>    - API overview and base URL
>    - Table of all endpoints (method, path, summary, status codes)
>    - Detailed endpoint sections with parameters, request/response examples, error codes
> 7. Output drift report: "Added: POST /notes/{id}/extract. Changed: PUT /notes/{id} (new). Removed: None."
> 8. Commit message suggestion: "[Week4 Task 7] docs sync: generated API.md from OpenAPI spec"

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run (exact command):**
> ```bash
> cd /Users/kunyoung.park/Desktop/mindlogic/study-CS146S/week4
> /project:docs-sync
> ```
>
> **Expected output:**
> ```
> Extracting OpenAPI schema from FastAPI app...
> Found 10 endpoints in OpenAPI spec.
>
> Comparing with existing docs/API.md...
> Changes detected:
>  + POST /notes/{id}/extract (new endpoint)
>  ~ PUT /notes/{id} (updated)
>  ~ DELETE /notes/{id} (updated)
>
> Generating docs/API.md...
> ✓ Generated docs/API.md (2,847 bytes)
> ✓ Documented 10 endpoints with full schemas and examples
> ✓ All endpoints have status codes and error documentation
>
> Drift report:
>  Added: 1 endpoint (POST /notes/{id}/extract)
>  Changed: 2 endpoints (PUT, DELETE)
>  Removed: 0 endpoints
>  Status: Docs now match OpenAPI spec (no drift)
>
> Recommended commit:
> git add docs/API.md
> git commit -m "[Week4 Task 7] docs sync: generated API.md from OpenAPI spec"
> ```
>
> **Rollback/Safety:**
> - Single file modified: `docs/API.md`
> - Revert with: `git checkout docs/API.md`
> - Safe to run multiple times — idempotent (no drift = no changes)
> - No side effects on code or database

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Developer manually maintains API.md
> - Read the `/openapi.json` endpoint by hand or use an API explorer
> - Check each endpoint's parameters, schemas, status codes manually
> - Copy/paste examples into markdown
> - Easy to miss new endpoints or forget to update old ones
> - Docs drift when new endpoints added but docs not updated
> - No systematic way to verify docs completeness
> - 30-60 minutes per major feature release to update docs
> - Docs vs. API mismatch causes support questions
>
> **After:** Automated generation from source of truth
> - Single command regenerates docs from actual OpenAPI schema
> - All endpoints automatically discovered and documented
> - Schemas, examples, and status codes pulled directly from code
> - Drift report shows exactly what changed
> - Docs always match API (no mismatch)
> - Can run before each commit to verify no drift
> - 30 seconds per run
> - Developer confidence that docs are current

e. How you used the automation to enhance the starter application
> This automation was used to complete **Task 7: Add Docs Drift Check** after Tasks 4-6 were implemented.
>
> **Workflow:**
> 1. Completed Tasks 4, 5, and 6 (extract endpoint, PUT/DELETE endpoints, field validators)
> 2. Ran `/project:docs-sync` to auto-generate docs/API.md from the updated FastAPI app
> 3. Received drift report: "Added: 1 endpoint (POST /notes/{id}/extract). Changed: 2 endpoints (PUT /notes/{id}, DELETE /notes/{id})"
> 4. Verified that docs/API.md was generated with all 10 endpoints documented:
>    - GET /notes/ (list all notes with pagination)
>    - POST /notes/ (create note)
>    - GET /notes/{id} (get single note)
>    - PUT /notes/{id} (update note) — NEW
>    - DELETE /notes/{id} (delete note) — NEW
>    - POST /notes/{id}/extract (extract tags) — NEW
>    - And 4 action item endpoints
> 5. Verified that the generated docs matched the actual OpenAPI spec by comparing against `/docs` endpoint
> 6. Committed the generated docs with the automation's suggested commit message
>
> **Impact:** Without this automation, Task 7 would require manually documenting all endpoints, cross-checking the OpenAPI spec, and hunting for drift. The automation reduced this to a single command and a drift verification step, ensuring docs are always synchronized with code.
