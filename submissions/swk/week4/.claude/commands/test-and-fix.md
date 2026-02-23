# Test-and-Fix Automation Loop

Run tests, analyze failures, fix source code, and ensure lint compliance in an iterative loop.

**Target directory**: `submissions/swk/week4/`
**Test filter (optional)**: $ARGUMENTS

## Safety Guardrails

- **Max iterations**: Retry the test→fix cycle at most **5 times**. If tests still fail after 5 attempts, stop and report what was tried.
- **Do NOT modify test files** (`backend/tests/test_*.py`, `backend/tests/conftest.py`) unless the user explicitly included "fix tests" or "update tests" in $ARGUMENTS.
- **Do NOT delete files or remove existing functionality.** Only make targeted fixes to the specific code causing failures.
- **Do NOT modify the Makefile, pyproject.toml, or any configuration files.**
- **Always preserve existing passing behavior.** If a fix would break other tests, find an alternative approach.
- **Before editing any file, read it first** to understand the full context.

## Step-by-Step Procedure

### Step 1: Run Tests

Change to the `submissions/swk/week4/` directory and run tests.

If $ARGUMENTS is provided and non-empty, use it as the test target:
```bash
cd submissions/swk/week4 && PYTHONPATH=. pytest -q $ARGUMENTS --tb=short 2>&1
```

If $ARGUMENTS is empty, run the full test suite:
```bash
cd submissions/swk/week4 && PYTHONPATH=. pytest -q backend/tests --tb=short 2>&1
```

### Step 2: Evaluate Test Results

- If **all tests pass**, proceed to **Step 4** (Lint Check).
- If **any tests fail**, proceed to **Step 3** (Analyze and Fix).

### Step 3: Analyze Failures and Fix Code

For each failing test:

1. **Read the full traceback** carefully. Identify the exact assertion or exception.
2. **Read the test file** to understand what behavior is expected.
3. **Read the source file** being tested (routers, models, schemas, services, etc.).
4. **Identify the root cause**: Is it a missing endpoint? Wrong status code? Missing field? Logic error? Import error?
5. **Apply a minimal, targeted fix** to the source code (NOT the test file, unless explicitly allowed).
6. **Log what you changed** and why.

After applying fixes, return to **Step 1** to re-run the tests. Track the iteration count.

If the iteration count reaches **5** and tests still fail:
- Stop the loop.
- Report all changes made so far.
- Report remaining failures with analysis.
- Suggest next steps for the user.

### Step 4: Lint Check

Run the linter:
```bash
cd submissions/swk/week4 && ruff check . 2>&1
```

- If **lint passes** (no errors), proceed to **Step 6** (Summary).
- If **lint fails**, proceed to **Step 5** (Auto-format).

### Step 5: Auto-Format and Re-Lint

Run the formatter and fixer:
```bash
cd submissions/swk/week4 && black . && ruff check . --fix 2>&1
```

Then re-run lint to confirm:
```bash
cd submissions/swk/week4 && ruff check . 2>&1
```

If lint still fails after auto-formatting, analyze remaining errors and fix manually. If unresolvable after 3 format-fix cycles, report the remaining issues.

### Step 6: Final Summary

Produce a clear summary report:

```
=== Test-and-Fix Report ===

Test Results:
- Tests run: X | Passed: Y | Failed: Z
- Files tested: [list of test files]

Fixes Applied:
- [file path]: [what changed] — [why]

Lint Status: PASS / FAIL
- [any formatting changes applied]

Iterations Used: N / 5

Remaining Issues:
- [any unresolved problems + suggested next steps]
```
