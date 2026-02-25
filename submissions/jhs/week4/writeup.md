# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Jaeho Shin** \
SUNet ID: **jhs** \
Citations: **Anthropic Claude Code Best Practices (https://www.anthropic.com/engineering/claude-code-best-practices), Anthropic SubAgents Docs (https://docs.anthropic.com/en/docs/claude-code/sub-agents)**

This assignment took me about **4** hours to do.


## YOUR RESPONSES
### Automation #1: `/project:test-runner` — Test Runner with Coverage
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **Claude Code Best Practices** article, specifically the section on custom slash commands for repeated workflows. The article recommends creating focused, idempotent commands that wrap common developer tasks. The example of a "test runner with coverage" in the assignment spec (Example 1 under Section A) directly motivated this design. I also followed the best practice of keeping commands **read-only** and **safe to run repeatedly** without side effects.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Automate the test → coverage → diagnosis workflow into a single command, eliminating the need to manually run pytest, interpret failures, check coverage, and identify gaps.
>
> **Inputs:** Optional `$ARGUMENTS` for pytest markers or specific test paths (e.g., `-k test_notes` or `backend/tests/test_extract.py`).
>
> **Outputs:**
> - Test summary: X passed, Y failed, Z skipped
> - Coverage percentage per module
> - List of files below 80% coverage with uncovered line numbers
> - For failures: root cause analysis and suggested code fixes
> - For low coverage: proposed new test functions with descriptive names
>
> **Steps:**
> 1. Run `pytest -q backend/tests --maxfail=3 -x --tb=short` with optional arguments
> 2. If all pass, run `pytest --cov=backend/app --cov-report=term-missing`
> 3. Parse and summarize results
> 4. If failures: read failing test + source, diagnose root cause, suggest fix
> 5. If coverage < 80%: identify untested branches and propose test cases

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> ```bash
> # From the submissions/jhs/week4/ directory in Claude Code:
> /project:test-runner
> /project:test-runner -k test_notes
> /project:test-runner backend/tests/test_extract.py
> ```
>
> **Expected output:** A structured summary showing pass/fail counts, coverage percentages, and actionable suggestions for any failures or coverage gaps.
>
> **Safety/Rollback:** This command is entirely **read-only** — it never modifies source code, tests, or the database. Uses an isolated temporary SQLite database via conftest.py. Safe to run as many times as needed. No rollback necessary.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual):**
> 1. Run `make test` → read raw pytest output
> 2. If failures, manually open test file and source file to diagnose
> 3. Separately run `pytest --cov` for coverage
> 4. Manually scan coverage report for low-coverage modules
> 5. Mentally identify which branches/functions need tests
> 6. Total: ~5-10 minutes of context-switching per cycle
>
> **After (automated):**
> 1. Run `/project:test-runner` → get structured summary with diagnosis and suggestions in one shot
> 2. Total: ~30 seconds, zero context-switching

e. How you used the automation to enhance the starter application
> I used the test-runner automation (following its workflow) to systematically identify gaps in the starter app's test coverage. The original starter had only 3 test files with minimal coverage. After running the test analysis workflow, I:
> - Added 10 new test functions for notes (update, delete, extract, validation, edge cases)
> - Added 4 new test functions for action items (delete, not-found, validation)
> - Added 4 new test functions for the extract service (empty input, no matches, tag extraction)
> - Total test count went from **3 tests** to **24 tests** — an 8x improvement
> - Identified that the extract service had zero tag-parsing capability, which led to implementing `extract_tags()`


### Automation #2: `/project:docs-sync` — API Documentation Synchronizer
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **Claude Code Best Practices** article's emphasis on keeping documentation in sync with code. The assignment spec's Example 2 (Docs sync) was the direct template. The best practices article warns about "docs drift" — when API documentation falls out of date with the actual implementation. This automation addresses that by reading the source of truth (router files) and generating documentation that exactly matches the real endpoints.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Automatically generate and maintain `docs/API.md` from the actual FastAPI router definitions, detecting any drift between docs and code.
>
> **Inputs:** Optional `$ARGUMENTS` — pass `--check-only` to only report drift without writing changes.
>
> **Outputs:**
> - Updated `docs/API.md` with all endpoints, schemas, request/response formats
> - Drift report: new endpoints, removed endpoints, changed parameters
> - Diff-like summary of what changed
>
> **Steps:**
> 1. Read `backend/app/main.py` to find all registered routers
> 2. Read each router file to catalog endpoints (method, path, body, response, status)
> 3. Read `backend/app/schemas.py` to document Pydantic models
> 4. Read existing `docs/API.md` if it exists
> 5. Generate updated API.md in a standardized table format
> 6. Compare old vs. new and report drift
> 7. Write the updated file (unless `--check-only`)

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> ```bash
> # From the submissions/jhs/week4/ directory in Claude Code:
> /project:docs-sync
> /project:docs-sync --check-only
> ```
>
> **Expected output:** A newly generated or updated `docs/API.md` with tables describing all endpoints and schemas, plus a drift report showing what changed.
>
> **Safety/Rollback:** Only modifies `docs/API.md` — never touches source code or tests. To rollback: `git checkout docs/API.md`. Idempotent: running multiple times produces the same output.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual):**
> 1. Add/change an endpoint in a router file
> 2. Remember to update docs (often forgotten)
> 3. Manually open `docs/API.md` and find the right section
> 4. Write the endpoint documentation by hand, cross-referencing schemas.py
> 5. Hope you didn't miss anything or make a typo
> 6. No way to detect if docs are already stale
>
> **After (automated):**
> 1. Make code changes
> 2. Run `/project:docs-sync` → docs are regenerated from source
> 3. Drift report immediately shows what changed
> 4. Zero chance of docs being out of sync with code

e. How you used the automation to enhance the starter application
> I used the docs-sync automation workflow to generate `docs/API.md` from scratch for the enhanced starter app. The original starter had no API documentation at all — just a `TASKS.md` todo list. After adding all the new endpoints (PATCH, DELETE for notes, DELETE for action items, POST extract), I ran the docs-sync workflow to produce a comprehensive API reference that documents:
> - All 11 endpoints across Notes and Action Items
> - Every Pydantic schema with field types and validation constraints
> - HTTP status codes for success and error cases
> - Request body and response model references


### *(Optional) Automation #3: `CLAUDE.md` Guidance File*
*Week4-specific CLAUDE.md providing code navigation, style guardrails, and workflow guidance.*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **Claude Code Best Practices** article's section on `CLAUDE.md` files as "repository-specific instructions." The article emphasizes that CLAUDE.md should be treated like a prompt — concise, actionable, and iterated upon. The assignment spec's Section B examples (code navigation, style guardrails, workflow snippets) guided the structure.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Provide Claude with deep context about the week4 application so it can navigate the codebase, follow coding conventions, and execute proper workflows without manual guidance each session.
>
> **Contents:**
> - **Project Structure:** File-by-file map of the codebase with purpose annotations
> - **Running the App:** Exact make commands and URLs
> - **Code Style Rules:** Line length, formatter, linter, Python version, type hint conventions
> - **Architecture Patterns:** Dependency injection, Pydantic v2 usage, HTTP status codes, test isolation
> - **Workflow: Adding a New Endpoint:** 8-step TDD workflow (write failing test → implement → format → update docs)
> - **Workflow: Fixing a Bug:** 4-step reproduce → fix → test → lint workflow
> - **Safety Guardrails:** Commands to never run (DROP TABLE, delete DB), always-use practices (parameterized queries, pre-commit tests)

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:** The CLAUDE.md is automatically loaded when starting a Claude Code session in the `submissions/jhs/week4/` directory. No manual command needed.
>
> **Expected output:** Claude's behavior is shaped by the guidance — it follows TDD workflows, uses correct make commands, respects style rules, and avoids destructive operations.
>
> **Rollback:** `git checkout CLAUDE.md` or simply delete the file to remove guidance.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (without CLAUDE.md):**
> - Had to tell Claude the project structure every session
> - Claude might use `List[X]` instead of `list[X]`, or forget to run `make format`
> - No enforced workflow — Claude might skip writing tests first
> - Risk of destructive commands (deleting DB, dropping tables)
>
> **After (with CLAUDE.md):**
> - Claude immediately knows the codebase layout, conventions, and workflows
> - Follows TDD: writes failing test → implements → formats → syncs docs
> - Respects style rules (100 char lines, black, ruff, modern type hints)
> - Safety guardrails prevent accidental data loss

e. How you used the automation to enhance the starter application
> The CLAUDE.md guided the entire enhancement process. By having the "Workflow: Adding a New Endpoint" steps baked in, every new feature I added followed the same disciplined pattern: write failing test first, implement the feature, run format/lint, update docs. This resulted in consistent, well-tested code across all enhancements (PATCH/DELETE notes, DELETE action items, extract endpoint, validation rules). The safety guardrails also prevented any accidental data loss during development.
