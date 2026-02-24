# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## YOUR RESPONSES
### Automation #1: `/test-and-fix` (Custom Slash Command)
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) guide, specifically the principles of building **reusable slash commands** for repeated workflows and preferring **idempotent, safe operations**. The test-fix-retest loop is one of the most common developer cycles, and automating it with Claude Code reduces manual context-switching between reading errors, editing code, and re-running tests.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Automatically run tests, analyze failures, fix the implementation code, apply formatting/linting, and re-test — all in a single command.
>
> **Inputs**: Optional test pattern via `$ARGUMENTS` (e.g., `test_notes` to filter specific tests).
>
> **Outputs**: Summary of original failures, list of modified files, fixes applied, and final test results.
>
> **Steps**:
> 1. Run `make test` (or filtered `pytest -k $ARGUMENTS`) and capture output
> 2. If all tests pass, report success and stop
> 3. If tests fail: read failing test files to understand expected behavior, then read the corresponding implementation files
> 4. Apply minimal, focused fixes to implementation code only (never modify tests)
> 5. Run `make format` (black + ruff --fix) and `make lint`
> 6. Re-run `make test` to verify (max 3 iterations)
> 7. Report final status with rollback instructions

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Run**: In Claude Code, type `/test-and-fix` (all tests) or `/test-and-fix test_notes` (specific pattern).
>
> **Expected output**: A structured report showing original failures, files changed, fixes applied, and final pass/fail status.
>
> **Rollback**: `git restore submissions/mjk/week4/backend/app/` to undo all implementation changes.
>
> **Safety**: Only modifies files under `backend/app/`, never touches test files, limits to 3 fix iterations to prevent infinite loops.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**:
> 1. Run `make test` in terminal
> 2. Read error output, identify failing test
> 3. Open the test file to understand the expectation
> 4. Open the implementation file to find the bug
> 5. Make a code change
> 6. Run `make format` and `make lint`
> 7. Run `make test` again
> 8. If still failing, repeat steps 2-7
>
> **After (automated)**: Run `/test-and-fix` once — Claude handles the entire loop automatically, reading tests, tracing code, applying fixes, formatting, and re-testing. The developer reviews the final summary and approves or rolls back.

e. How you used the automation to enhance the starter application
> After writing failing tests for `PUT /notes/{note_id}` and `DELETE /notes/{note_id}` (TASKS.md #5), I ran `/test-and-fix`. Claude analyzed the 4 failing tests (405 Method Not Allowed), identified that the router was missing these endpoints, and automatically added `update_note` and `delete_note` to `backend/app/routers/notes.py` following the existing code patterns (dependency injection, 404 handling, Pydantic validation). It then ran `make format` and `make lint` to ensure code quality, and re-ran `make test` — all 7 tests passed. The entire cycle from failure to green took a single command instead of manual back-and-forth.


### Automation #2: `/docs-sync` (Custom Slash Command)
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) section on keeping documentation in sync with code, and directly modeled after the assignment's suggested "Docs sync" example. Documentation drift — where API docs fall behind actual implementation — is a common problem in fast-moving projects. By reading the live OpenAPI spec that FastAPI auto-generates, we ensure docs always reflect the actual running code.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Automatically generate/update `docs/API.md` from the FastAPI OpenAPI spec, and show a clear diff of route changes.
>
> **Inputs**: None (requires the server to be running on localhost:8000).
>
> **Outputs**: Updated `docs/API.md` file and a route delta summary (added/removed/modified routes).
>
> **Steps**:
> 1. Check if the server is running on localhost:8000; if not, start it in the background
> 2. Fetch `/openapi.json` via curl
> 3. Read existing `docs/API.md` (if present) to capture the old route list
> 4. Parse the OpenAPI JSON — extract routes, methods, parameters, request/response schemas
> 5. Generate a well-structured `docs/API.md` organized by tags (Notes, Action Items), including schemas table
> 6. Compare old vs new routes and present a diff summary (added, removed, modified)
> 7. Write the updated file and report the summary

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Pre-requisite**: Server must be running (`make run`), or the command will auto-start it.
>
> **Run**: In Claude Code, type `/docs-sync`.
>
> **Expected output**: A route delta summary like:
> ```
> Route Delta Summary:
>   Added:    PUT /notes/{note_id}
>   Added:    DELETE /notes/{note_id}
>   Removed:  (none)
> Updated: docs/API.md
> ```
>
> **Rollback**: `git restore docs/API.md` to revert documentation changes.
>
> **Safety**: Only modifies `docs/API.md`, never touches source code. Idempotent — safe to run multiple times.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**:
> 1. Open `http://localhost:8000/docs` in browser to view Swagger UI
> 2. Manually create or edit `docs/API.md`
> 3. Copy endpoint details one by one (path, method, parameters, schemas)
> 4. Compare with previous version to check what changed
> 5. Easy to miss routes or introduce inconsistencies
>
> **After (automated)**: Run `/docs-sync` — Claude fetches the live OpenAPI spec, generates the full API.md, and shows exactly which routes were added, removed, or modified. Zero manual copying, zero drift.

e. How you used the automation to enhance the starter application
> After adding the PUT/DELETE endpoints via `/test-and-fix`, I ran `/docs-sync` to generate `docs/API.md` from scratch (TASKS.md #7). The command fetched the live OpenAPI spec from `localhost:8000/openapi.json`, parsed all 10 routes (including the newly added PUT and DELETE), and generated a comprehensive API reference organized by tags (Root, Notes, Action Items) with full schema tables. Since this was the first generation, all routes were reported as "Added" in the delta summary. The starter app now has up-to-date API documentation that can be re-synced with a single command whenever endpoints change.


### *(Optional) Automation #3: `CLAUDE.md` (Guidance File)*
*Supporting automation that enhances the quality of Automation #1 and #2.*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Based on the [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) recommendation to use `CLAUDE.md` files for repository-specific instructions. The file is automatically loaded when Claude Code starts a conversation in the `week4/` directory, providing project context without manual explanation.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Provide Claude Code with project structure, commands, development patterns, code style rules, and safety guidelines so that slash commands execute with full context.
>
> **Contents**: Project structure map, Makefile commands, development workflow patterns (how to add endpoints, how to fix tests), code style rules (black/ruff, 100-char lines), and safety boundaries (what's safe to automate vs. what needs confirmation).

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Run**: Automatically loaded by Claude Code when working in `week4/`. No manual command needed.
>
> **Location**: `submissions/mjk/week4/CLAUDE.md`
>
> **Rollback**: `git restore submissions/mjk/week4/CLAUDE.md`

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before**: Every time you start a Claude Code session, you'd need to explain: "tests are in backend/tests/, run make test, use black for formatting, don't modify test files..." etc.
>
> **After**: Claude automatically knows the project structure, conventions, and safety rules. Slash commands like `/test-and-fix` and `/docs-sync` work more accurately because Claude understands the project context.

e. How you used the automation to enhance the starter application
> The `CLAUDE.md` file provided context that made both `/test-and-fix` and `/docs-sync` work accurately on the first try. For example, `/test-and-fix` knew to look in `backend/app/routers/` for implementation files and to follow the existing dependency injection pattern (`Depends(get_db)`), while `/docs-sync` knew the Makefile commands and where to write `docs/API.md`. Without this guidance file, each slash command would require manual explanation of the project structure every time.
