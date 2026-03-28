---
description: Analyze changes, format code, organize commits, and create a pull request
allowed-tools: Bash, Read, Glob, Grep
---

# Create Pull Request

Streamline the entire PR workflow: analyze changes, format, commit logically, and submit.

Arguments: $ARGUMENTS (e.g., PR title or description hint. If empty, auto-generate from changes.)

## Steps

### 1. Analyze Current State

- Run `git status` to see all changed, staged, and untracked files
- Run `git diff` (staged + unstaged) to understand what changed
- Identify the current branch and base branch (usually `main`)
- Summarize changes by category (new features, bug fixes, docs, tests, config)

### 2. Format and Lint

- If a Makefile exists with `format`/`lint` targets, run them: `make format && make lint`
- Otherwise, check for common formatters (black, prettier, rustfmt) and run them
- Fix any auto-fixable lint issues
- Report if there are remaining lint errors that need manual attention

### 3. Organize Commits

Group changes into logical commits. Principles:
- Separate concerns: tests apart from implementation, docs apart from code
- Each commit should make sense on its own
- Use conventional commit style: `feat:`, `fix:`, `docs:`, `test:`, `chore:`

For each logical group:
- Stage the relevant files with `git add <specific files>`
- Commit with a clear, descriptive message

### 4. Push and Create PR

- Push the branch: `git push -u origin <branch-name>`
- Create the PR with `gh pr create`:
  - **Title:** Short, descriptive (under 70 chars). Use `$ARGUMENTS` if provided.
  - **Body:** Include:
    - `## Summary` — bullet points of what changed
    - `## Changes` — list of files modified, grouped by purpose
    - `## Test plan` — how to verify (e.g., `make test`)

### 5. Report

Output:
- PR URL
- Number of commits created
- Summary of changes included
- Any warnings (untracked files not included, lint issues, etc.)

## Guidelines

- Never force push
- Never commit `.env`, credentials, or secrets
- If there are merge conflicts with the base branch, stop and report them
- Ask for confirmation before pushing if there are more than 10 changed files
