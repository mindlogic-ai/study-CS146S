# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Min Jae Kim** \
SUNet ID: **mjk** \
Citations: Claude Code (AI coding assistant)

This assignment took me about **2** hours to do.

> Note: The requirement to split tasks into 4 separate PRs has been removed from the assignment. All tasks are submitted in a single PR.

## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> See PR linked below — all changes in a single commit.

b. PR Description
> Added DELETE endpoints for both Notes and Action Items with proper 404 handling. Added `/count` endpoints for both resources with optional filtering support. Implemented Pydantic Field-based input validation (min_length, max_length) on all create/patch schemas. Added `Path(gt=0)` validation on path parameters and `Query(ge=0)` on skip parameter. Added tests for delete, count, and validation (422 on empty/oversized inputs).

c. Graphite Diamond generated code review
> TODO (will be filled after PR is created and Graphite review is generated)

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> See PR linked below — all changes in a single commit.

b. PR Description
> Enhanced `extract_action_items()` to return structured dicts with metadata (priority, assignee, has_deadline) instead of plain strings. Added support for additional prefixes (FIX, BUG, TASK, HACK, follow-up), checkbox patterns (`[ ]`/`[x]`), priority keyword detection (urgent, critical, etc.), `@mention` assignee extraction, and deadline pattern recognition (by Friday, due 2024-01-01). Added `POST /notes/{id}/extract-actions` endpoint to extract action items from a note's content. Comprehensive tests covering all new patterns.

c. Graphite Diamond generated code review
> TODO (will be filled after PR is created and Graphite review is generated)

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> See PR linked below — all changes in a single commit.

b. PR Description
> Created a `Tag` model with a many-to-many relationship to `Note` via a `note_tags` association table with CASCADE deletes. Added full CRUD endpoints for tags (`/tags/`) with duplicate name prevention (409 Conflict). Extended Note create/patch to accept `tag_ids` for linking tags, with validation that all referenced tags exist. NoteRead response now includes nested tag objects. Tests cover tag CRUD, duplicate prevention, note-tag association, and invalid tag reference handling.

c. Graphite Diamond generated code review
> TODO (will be filled after PR is created and Graphite review is generated)

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> See PR linked below — all changes in a single commit.

b. PR Description
> Added comprehensive pagination tests for both Notes and Action Items: boundary cases (first page, middle page, last partial page, skip beyond total). Added sorting tests verifying ascending/descending order by various fields (title, description, created_at) and fallback behavior for invalid sort fields. Added combined filter+pagination tests for Action Items (completed filter with limit/skip). Total test count increased from 3 to 30.

c. Graphite Diamond generated code review
> TODO (will be filled after PR is created and Graphite review is generated)

## Brief Reflection
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> My manual review focused on: (1) **API shape** — ensuring route ordering to prevent path conflicts (e.g., `/count` before `/{id}`), (2) **correctness** — verifying that validation constraints match the model constraints (e.g., title max_length=200 in both schema and model), (3) **test gaps** — checking edge cases like empty inputs, non-existent IDs, and boundary pagination, (4) **security** — ensuring proper input validation to prevent injection of invalid data.

b. A comparison of **your** comments vs. **Graphite's** AI-generated comments for each PR.
> TODO (will be filled after Graphite review)

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO (will be filled after Graphite review)

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> I'm fairly comfortable using AI reviews for catching surface-level issues (naming, formatting, missing edge cases in tests) but still prefer manual review for architectural decisions, security implications, and business logic correctness. My heuristic: trust AI reviews for "what" issues (missing tests, unused imports) but verify manually for "why" issues (design trade-offs, performance implications).
