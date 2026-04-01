# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: SWK\
SUNet ID: NOPE \
Citations: Claude Code
This assignment took me about 0.5 hours to do. 


## YOUR RESPONSES
### Automation #1: `/test-and-fix` Custom Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the Claude Code best practices guide
> (https://www.anthropic.com/engineering/claude-code-best-practices), which emphasizes
> iterative test-driven workflows where Claude runs tests, analyzes failures, and applies
> fixes in a loop. The command design follows the recommended pattern of keeping slash
> commands focused on a single workflow, using `$ARGUMENTS` for flexibility, and preferring
> idempotent steps (as noted in the assignment tips). Safety guardrails (max retries,
> restricted file modifications) follow best practices for autonomous agent safety.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Automate the TDD red→green→refactor cycle. Given a codebase where tests may
> be failing, the command iteratively runs tests, diagnoses failures from tracebacks,
> applies minimal source-code fixes, and re-runs until green — then runs lint/format
> checks and auto-fixes any style violations.
>
> **Inputs**: Optional `$ARGUMENTS` — a test file path (e.g., `backend/tests/test_notes.py`),
> a pytest marker (e.g., `-k test_create`), or empty for the full suite.
>
> **Outputs**: A structured summary reporting: tests run/passed/failed, each fix applied
> (file, change, rationale), lint status, iteration count, and any remaining issues.
>
> **Steps**:
> 1. Run `pytest` (optionally filtered by `$ARGUMENTS`) from `submissions/swk/week4/`
> 2. If all tests pass → skip to step 4
> 3. If tests fail → read tracebacks → read relevant source files → apply targeted fix
>    to source code (not tests) → go back to step 1 (max 5 iterations)
> 4. Run `ruff check .` for lint validation
> 5. If lint fails → run `black . && ruff check . --fix` → re-check
> 6. Produce final summary report

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Run the full suite:**
> ```
> /test-and-fix
> ```
>
> **Run a specific test file:**
> ```
> /test-and-fix backend/tests/test_notes.py
> ```
>
> **Run a specific test by name:**
> ```
> /test-and-fix -k test_create_and_list_notes
> ```
>
> **Allow test file modifications:**
> ```
> /test-and-fix fix tests backend/tests/test_notes.py
> ```
>
> **Expected output example:**
> ```
> === Test-and-Fix Report ===
> Test Results: 6 passed, 0 failed (backend/tests/)
> Fixes Applied:
>   - backend/app/routers/notes.py: Added PUT /notes/{id} endpoint
>   - backend/app/schemas.py: Added NoteUpdate schema
> Lint Status: PASS (black auto-formatted 2 files)
> Iterations: 2 / 5
> Remaining Issues: None
> ```
>
> **Safety/Rollback notes**:
> - Will not modify test files unless "fix tests" appears in the arguments
> - Maximum 5 retry iterations to prevent infinite loops
> - Only source code under `backend/app/` is modified; no config files are touched
> - All changes can be reverted with `git checkout -- submissions/swk/week4/backend/app/`
> - The command does not commit any changes — review with `git diff` before committing

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual workflow):**
> 1. Run `make test` from the week4 directory
> 2. Read pytest output, scroll through tracebacks manually
> 3. Open the failing test file to understand expected behavior
> 4. Open the source file and trace the code path mentally
> 5. Make an edit, save, re-run `make test`
> 6. If still failing, repeat steps 2-5 (often multiple times)
> 7. Once tests pass, run `make lint`
> 8. If lint fails, run `make format`, then `make lint` again
> 9. Manually resolve any remaining lint issues
> 10. Total: ~10-30 minutes per failing test, high context-switching cost
>
> **After (automated workflow):**
> 1. Type `/test-and-fix` (optionally with a test filter)
> 2. Claude automatically executes the full test→fix→lint cycle
> 3. Receive a structured summary of all changes made
> 4. Review changes with `git diff` and commit
> 5. Total: ~1-3 minutes, minimal developer attention needed

e. How you used the automation to enhance the starter application
> I used the `/test-and-fix` workflow (manually simulated in this session) to implement
> three TASKS.md features for the starter application:
>
> **Task 5 — Notes CRUD enhancements (PUT/DELETE):**
> Wrote 4 failing tests (`test_update_note`, `test_update_note_not_found`,
> `test_delete_note`, `test_delete_note_not_found`). The test-and-fix loop identified
> 405 Method Not Allowed errors, then added `NoteUpdate` schema in `schemas.py` and
> `PUT /notes/{id}` + `DELETE /notes/{id}` endpoints in `routers/notes.py`. All 4 tests
> passed after 1 iteration.
>
> **Task 6 — Request validation & error handling:**
> Wrote 2 failing tests (`test_create_note_empty_title_rejected`,
> `test_create_note_empty_content_rejected`). The loop identified that empty strings were
> accepted (201 instead of 422), then added `min_length=1` validation via `Field()` in
> `NoteCreate` and `ActionItemCreate` schemas. Tests passed immediately.
>
> **Task 2 — Case-insensitive search:**
> Wrote 1 failing test (`test_search_case_insensitive`). The loop identified that
> `Note.title.contains(q)` was case-sensitive, then replaced it with
> `func.lower(Note.title).contains(q.lower())` in the search endpoint. Test passed.
>
> **Final result**: 10 tests passing (up from 3), lint clean, with PUT/DELETE/validation/
> search improvements across backend and frontend.


### Automation #2: `CLAUDE.md` Guidance File
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the Claude Code best practices guide
> (https://www.anthropic.com/engineering/claude-code-best-practices), which recommends
> using `CLAUDE.md` files to provide repository-specific context, code navigation maps,
> and workflow instructions. The guide emphasizes that CLAUDE.md should be "like a prompt
> — iterated on, concise, and actionable." Nested CLAUDE.md files in subdirectories
> provide scoped context when working in specific parts of the codebase. The design also
> follows the assignment's Category B examples: code navigation/entry points, style/safety
> guardrails, and workflow snippets.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Provide Claude with automatic, always-on context about the week4 starter app
> so it follows project conventions, knows file locations, and uses correct workflow
> patterns — without the developer needing to explain these every time.
>
> **Inputs**: None — CLAUDE.md is read automatically when Claude Code starts a session
> in the `submissions/swk/week4/` directory.
>
> **Outputs**: Claude's behavior changes — it will:
> - Know where every file lives (routers, models, schemas, tests, frontend)
> - Follow the TDD workflow (test first → schema → model → router → lint)
> - Use correct style (100-char lines, SQLAlchemy 2.0 `select()`, Pydantic v2 `model_validate()`)
> - Respect safety guardrails (don't touch config files, don't delete seed data)
> - Understand current gaps from TASKS.md for prioritizing work
>
> **Design sections**:
> 1. **Quick Start** — exact commands to run/test/lint
> 2. **Code Navigation** — table mapping every layer to its file path and role
> 3. **Architecture Pattern** — request flow diagram and key patterns (DI, session lifecycle)
> 4. **Style & Safety Guardrails** — must-follow rules, safe commands, things to avoid
> 5. **Workflow: Adding a New Endpoint** — step-by-step TDD checklist
> 6. **Workflow: Adding a New Model/Resource** — full resource creation checklist
> 7. **Current Gaps** — known missing features from TASKS.md

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to use**: No explicit command needed. The file is read automatically by Claude Code.
>
> To verify it's being used, start a Claude Code session in the week4 directory and ask
> Claude about the project:
> ```
> cd submissions/swk/week4
> # Start Claude Code, then ask:
> "What endpoints does this app have?"
> "Add a DELETE /notes/{id} endpoint"
> ```
>
> **Expected behavior**: Claude should:
> - Reference exact file paths (e.g., `backend/app/routers/notes.py`)
> - Follow the TDD workflow (write test first, then implement)
> - Use correct patterns (`select()`, `model_validate()`, `status_code=201`)
> - Refuse to modify config files without explicit permission
>
> **Rollback**: Simply delete or rename `submissions/swk/week4/CLAUDE.md` to disable.
> The file is purely advisory and makes no code changes on its own.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (without CLAUDE.md):**
> 1. Start Claude Code session in the project
> 2. Claude doesn't know file structure — must explain where routers/models/tests live
> 3. Claude might use deprecated patterns (e.g., `from_orm()` instead of `model_validate()`)
> 4. Claude might use SQLAlchemy 1.x `query()` style instead of 2.0 `select()` style
> 5. Claude might skip tests, or write tests after implementation
> 6. Claude might modify config files or seed data unexpectedly
> 7. Every new conversation requires re-explaining project conventions
>
> **After (with CLAUDE.md):**
> 1. Start Claude Code session — context is loaded automatically
> 2. Claude already knows the full file map and architecture
> 3. Claude follows correct patterns (Pydantic v2, SQLAlchemy 2.0) from the start
> 4. Claude follows TDD workflow (test → schema → model → router → lint)
> 5. Claude respects safety guardrails without being told
> 6. Every conversation starts with the same consistent baseline knowledge

e. How you used the automation to enhance the starter application
> The `CLAUDE.md` file guided the entire development workflow during this session.
> Specifically:
>
> **TDD workflow enforcement**: Following the "Workflow: Adding a New Endpoint" section,
> all 3 features (PUT/DELETE, validation, search) were developed test-first. Failing
> tests were written before any source code was modified, matching the prescribed order:
> test → schema → model → router → lint.
>
> **Code navigation**: The code navigation table helped immediately locate the correct
> files to modify — `schemas.py` for `NoteUpdate`, `routers/notes.py` for new endpoints,
> and the search query logic — without exploring the directory structure each time.
>
> **Style guardrails**: All new code followed the documented patterns: SQLAlchemy 2.0
> `select()` style, Pydantic v2 `model_validate()`, `Field()` for validation,
> `Depends(get_db)` for dependency injection, and proper HTTP status codes (201 for
> creation, 404 for not found, 422 for validation errors).
>
> **Current gaps section**: The "Current Gaps" section directly mapped to TASKS.md and
> helped prioritize which features to implement first (PUT/DELETE, validation,
> case-insensitive search).


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> TODO

b. Design of each automation, including goals, inputs/outputs, steps
> TODO

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> TODO

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

e. How you used the automation to enhance the starter application
> TODO
