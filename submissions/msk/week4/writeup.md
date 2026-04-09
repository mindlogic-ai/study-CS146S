# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Min Seo Kim \
SUNet ID: idk \
Citations: **Claude Code best practices (anthropic.com/engineering/claude-code-best-practices), SubAgents overview (docs.anthropic.com/en/docs/claude-code/sub-agents), Claude Code documentation on custom slash commands and CLAUDE.md files**

This assignment took me about **1** hours to do.


## YOUR RESPONSES
### Automation #1: `CLAUDE.md` Guidance File (Category B)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the Claude Code best-practices doc (anthropic.com/engineering/claude-code-best-practices), which recommends creating a `CLAUDE.md` file with project structure descriptions, build/test commands, code style rules, and workflow patterns. The doc emphasizes that `CLAUDE.md` is "automatically read when starting a conversation" and should contain "repository-specific instructions, context, or guidance that influence Claude's behavior." I structured the file around the four key areas the docs recommend: project overview, how to run/test, style guardrails, and actionable workflow snippets.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Provide Claude with persistent, session-independent project context so every interaction benefits from knowledge of the directory layout, database schema, run commands, style rules, and known bugs -- without the developer having to re-explain the project each time.
>
> **Inputs**: None -- the file is automatically loaded when Claude Code starts in the `week4/` directory.
>
> **Outputs**: Influences Claude's behavior across all interactions. Claude follows TDD workflow patterns, runs format/lint correctly, knows the database schema, and is aware of existing bugs.
>
> **Sections created**:
> 1. Project Overview -- tech stack summary
> 2. Directory Layout -- full tree with annotations for every key file
> 3. How to Run -- exact `make` commands with prerequisites
> 4. Database Schema -- SQLite table definitions
> 5. Style and Safety Guardrails -- black/ruff rules, commands to always/never run
> 6. Workflow Patterns -- step-by-step guides for adding endpoints, validation, and services
> 7. Known Issues -- pre-identified bugs so Claude can proactively fix them
> 8. Testing Conventions -- fixture usage, file naming, run commands

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run**: No explicit command needed. Simply launch Claude Code from the `week4/` directory:
> ```bash
> cd week4/
> claude
> ```
> The `CLAUDE.md` file is automatically read on session start.
>
> **Expected output**: Claude's responses reflect project awareness. For example, asking "How do I run tests?" produces the correct `make test` command. Asking "Add a new endpoint" triggers the TDD workflow pattern from the file.
>
> **Rollback**: Delete `week4/CLAUDE.md` to remove all project-specific guidance. Claude reverts to default behavior with no project context.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before**: Every Claude Code session required manually explaining the project structure, specifying which formatter to use (black vs. autopep8), listing run commands, and describing database tables. Claude might suggest wrong file paths, skip linting, or write tests in the wrong location.
>
> **After**: Claude instantly knows the full project layout, follows the correct TDD workflow, uses the right format/lint commands, and is aware of existing bugs. Zero repetitive context-setting needed across sessions.

e. How you used the automation to enhance the starter application
> The `CLAUDE.md` file guided every subsequent automation. Its "Workflow Patterns" section ensured Claude followed TDD when implementing features via the `/project:tdd-feature` slash command. The "Known Issues" section let Claude proactively fix the case-sensitive search bug when asked about search. The "Style and Safety Guardrails" ensured `make format && make lint` was run after every code change.


### Automation #2: `/project:tdd-feature` Slash Command (Category A)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the Claude Code best-practices doc section on custom slash commands: "Slash commands are a feature for repeated workflows, letting you create reusable workflows in Markdown files inside `.claude/commands/`." Also drew from the TDD approach recommended in the assignment examples ("TestAgent writes/updates tests for a change -> CodeAgent implements code to pass tests -> TestAgent verifies"). The `$ARGUMENTS` feature lets each invocation target a different feature while following the same structured workflow.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Enforce a strict RED-GREEN-REFACTOR TDD cycle for any feature request, ensuring tests are always written before implementation.
>
> **Inputs**: `$ARGUMENTS` -- a natural-language feature description (e.g., "Add PUT /notes/{id} and DELETE /notes/{id} endpoints").
>
> **Outputs**: Failing tests (RED phase), passing implementation (GREEN phase), formatted/linted code, and a structured summary of all changes.
>
> **7-step workflow**:
> 1. **Analyze** -- Read relevant source files, identify files to modify, plan changes
> 2. **Write failing tests (RED)** -- Create tests in `backend/tests/`, run `make test` to confirm they FAIL
> 3. **Implement (GREEN)** -- Make minimal code changes to pass tests, run `make test` to confirm ALL pass
> 4. **Refactor (IMPROVE)** -- Review for clarity, remove duplication
> 5. **Format and lint** -- Run `make format && make lint`, fix any issues
> 6. **Update frontend** -- If the feature has UI implications, update `app.js`/`index.html`
> 7. **Summary** -- List files modified, tests added, endpoints changed, remaining TODOs

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run**: From Claude Code (launched in `week4/`):
> ```
> /project:tdd-feature Add PUT /notes/{id} and DELETE /notes/{id} endpoints
> ```
>
> **Expected output**: Claude walks through each step sequentially:
> - RED: Shows new test functions and `make test` output with failures
> - GREEN: Shows implementation code and `make test` output with all passing
> - IMPROVE: Shows any refactoring changes
> - Final summary listing all modified files and new test functions
>
> **Rollback**: `git checkout -- .` to revert all changes. Since the workflow is test-first, you can also safely delete just the new test functions and route handlers.
>
> **Safety notes**: The command is idempotent -- running it again with the same arguments will detect the feature already exists. It never modifies the database directly; all changes are to source code files.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before**: Developer manually decides where to put tests, writes code first (skipping TDD), sometimes forgets to run the linter, and doesn't verify tests fail before implementation. The workflow varies per developer and per session.
>
> **After**: Single command enforces a consistent 7-step TDD cycle every time. Tests are guaranteed to be written first and verified to fail. Format/lint is never skipped. The output summary creates an audit trail of exactly what changed.

e. How you used the automation to enhance the starter application
> Used `/project:tdd-feature` to implement four features from `docs/TASKS.md`:
> 1. **Case-insensitive search** (Task #2): `tdd-feature Make the search endpoint case-insensitive` -- added test `test_search_case_insensitive`, fixed `notes.py` to use `func.lower()`
> 2. **Tag extraction** (Task #4): `tdd-feature Add extract_tags() to parse #tag syntax` -- added 4 tests (`test_extract_tags_basic`, `_deduplication`, `_empty`, `_multiline`), implemented `extract_tags()` in `extract.py`
> 3. **CRUD enhancements** (Task #5): `tdd-feature Add PUT /notes/{id} and DELETE /notes/{id}` -- added 4 tests (`test_update_note`, `_not_found`, `test_delete_note`, `_not_found`), implemented both endpoints, updated frontend with Edit/Delete buttons
> 4. **Input validation** (Task #6): `tdd-feature Add validation: title 1-200 chars, content/description non-empty` -- added 4 tests (`test_create_note_empty_title`, `_empty_content`, `_title_too_long`, `test_create_action_item_empty_description`), added `Field()` constraints to schemas


### *(Optional) Automation #3*: `/project:docs-sync` Slash Command (Category A)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Directly inspired by the assignment's Example 2 for slash commands: "Read `/openapi.json`, update `docs/API.md`, and list route deltas." Also addresses Task #7 from `docs/TASKS.md`: "Create/maintain a simple `API.md` describing endpoints and payloads. After each change, verify docs match actual OpenAPI." The Claude Code best-practices doc recommends "idempotent steps" in slash commands, which this workflow follows -- running it multiple times converges to the same correct output.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Generate and maintain `docs/API.md` that accurately reflects the actual API, and detect documentation drift.
>
> **Inputs**: None (reads the codebase directly).
>
> **Outputs**: Updated `docs/API.md` with all endpoints documented, plus a drift report listing new/removed/changed endpoints.
>
> **6-step workflow**:
> 1. **Discover routes** -- Read `main.py` and all router files to catalog every endpoint (method, path, params, schema, status code)
> 2. **Read existing docs** -- Check if `docs/API.md` exists and parse current contents
> 3. **Read Pydantic schemas** -- Read `schemas.py` to document request/response shapes with validation constraints
> 4. **Generate/update API.md** -- Write structured documentation grouped by resource
> 5. **Drift report** -- Compare new vs. old docs, report new/removed/changed endpoints
> 6. **Verify** -- Run `make test` to confirm no code was accidentally changed

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run**: From Claude Code (launched in `week4/`):
> ```
> /project:docs-sync
> ```
>
> **Expected output**: Claude reads all router files, generates/updates `docs/API.md`, and prints a drift report:
> ```
> Drift Report:
> - New endpoints: PUT /notes/{note_id}, DELETE /notes/{note_id}
> - Changed: NoteCreate now has validation constraints (min_length, max_length)
> - Changed: ActionItemCreate now has validation constraints (min_length)
> ```
>
> **Rollback**: `git checkout docs/API.md` to revert to previous version.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before**: Developer must manually inspect every router file, cross-reference with schema definitions, write markdown by hand, and remember to update docs after every endpoint change. Documentation easily becomes stale and inaccurate.
>
> **After**: Single command regenerates documentation from the source of truth (the actual code) and explicitly reports what changed. Running it after any code change ensures docs stay in sync.

e. How you used the automation to enhance the starter application
> Ran `/project:docs-sync` twice:
> 1. **Initial run** (before any code changes): Created `docs/API.md` documenting the 6 original endpoints. All reported as "New" since no previous docs existed.
> 2. **Second run** (after implementing all features): Updated `docs/API.md` to include the 2 new endpoints (PUT/DELETE notes) and updated schema documentation to reflect validation constraints (title: min 1/max 200, content: min 1, description: min 1). Drift report showed 2 new endpoints and 2 changed schemas.
