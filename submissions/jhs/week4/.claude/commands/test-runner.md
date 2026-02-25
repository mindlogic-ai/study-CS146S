# Test Runner with Coverage

Run the test suite, report results, and suggest fixes for any failures.

## Instructions

1. **Run the tests** from the `submissions/jhs/week4/` directory:
   ```bash
   cd submissions/jhs/week4 && PYTHONPATH=. pytest -q backend/tests --maxfail=3 -x --tb=short $ARGUMENTS
   ```

2. **If all tests pass**, run coverage analysis:
   ```bash
   cd submissions/jhs/week4 && PYTHONPATH=. pytest --cov=backend/app --cov-report=term-missing backend/tests $ARGUMENTS
   ```

3. **Summarize results** in this format:
   - Total tests: X passed, Y failed, Z skipped
   - Coverage: X% overall
   - Files with lowest coverage (list any below 80%)

4. **If any tests fail**:
   - Read the failing test file and the source file it tests
   - Identify the root cause of each failure
   - Suggest a concrete fix (show the code change needed)
   - Do NOT automatically apply fixes — just suggest them

5. **If coverage is below 80%**, suggest new test cases:
   - Identify untested functions/branches
   - Propose specific test functions with descriptive names
   - Focus on edge cases and error paths

## Safety
- This command is **read-only** — it never modifies source code
- Safe to run repeatedly without side effects
- Uses a temporary SQLite database for test isolation (see conftest.py)
