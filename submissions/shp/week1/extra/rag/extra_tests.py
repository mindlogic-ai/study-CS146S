import os
import re
import sys
from typing import Callable, List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag import YOUR_SYSTEM_PROMPT, YOUR_CONTEXT_PROVIDER, CORPUS

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RUNS_PER_TEST = 3

# (question, required_snippets, description)
# Different API coding tasks using the same API docs context
TEST_CASES: List[Tuple[str, List[str], str]] = [
    # Original test case
    (
        "Write a Python function `fetch_user_name(user_id: str, api_key: str) -> str` that calls "
        "the documented API to fetch a user by id and returns only the user's name as a string.",
        ["def fetch_user_name(", "requests.get", "/users/", "X-API-Key", "return"],
        "fetch user name",
    ),
    # Variant: just fetch user data
    (
        "Write a Python function `get_user(user_id: str, api_key: str) -> dict` that calls "
        "the documented API to fetch a user by id and returns the full user data as a dictionary.",
        ["def get_user(", "requests.get", "/users/", "X-API-Key", "return"],
        "get full user dict",
    ),
    # Variant: check if user exists
    (
        "Write a Python function `user_exists(user_id: str, api_key: str) -> bool` that calls "
        "the documented API and returns True if the user exists (200 response), False otherwise.",
        ["def user_exists(", "requests.get", "/users/", "X-API-Key", "return"],
        "check user exists",
    ),
    # Test that it uses correct base URL
    (
        "Write a Python function `fetch_user_id(user_id: str, api_key: str) -> str` that calls "
        "the documented API to fetch a user by id and returns only the user's id as a string.",
        ["def fetch_user_id(", "api.example.com", "X-API-Key", "return"],
        "uses correct base URL",
    ),
]


def make_user_prompt(question: str, context_docs: List[str]) -> str:
    if context_docs:
        context_block = "\n".join(f"- {d}" for d in context_docs)
    else:
        context_block = "(no context provided)"
    return (
        f"Context (use ONLY this information):\n{context_block}\n\n"
        f"Task: {question}\n\n"
        "Requirements:\n"
        "- Use the documented Base URL and endpoint.\n"
        "- Send the documented authentication header.\n"
        "- Raise for non-200 responses.\n"
        "- Return the appropriate value.\n\n"
        "Output: A single fenced Python code block with the function and necessary imports.\n"
    )


def extract_code_block(text: str) -> str:
    """Extract the last fenced Python code block."""
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()


def test_single_case(
    question: str, required_snippets: List[str], description: str
) -> Tuple[bool, int, List[List[str]]]:
    """Test a single case multiple times.

    Returns: (all_passed, success_count, missing_snippets_per_run)
    """
    context_docs = YOUR_CONTEXT_PROVIDER(CORPUS)
    user_prompt = make_user_prompt(question, context_docs)

    all_missing: List[List[str]] = []
    success_count = 0

    for _ in range(RUNS_PER_TEST):
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=YOUR_SYSTEM_PROMPT,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        code = extract_code_block(response.text)
        missing = [s for s in required_snippets if s not in code]
        all_missing.append(missing)

        if not missing:
            success_count += 1

    all_passed = success_count == RUNS_PER_TEST
    return all_passed, success_count, all_missing


def run_all_tests() -> None:
    """Run all test cases and print results."""
    print("=== RAG Extra Tests ===\n")

    total_cases = len(TEST_CASES)
    passed_cases = 0
    total_runs = 0
    total_successes = 0

    for question, required_snippets, description in TEST_CASES:
        display_q = question[:50] + "..." if len(question) > 50 else question
        print(f"Test: {display_q}")
        print(f"  Description: {description}")
        print(f"  Required: {required_snippets}")

        all_passed, success_count, all_missing = test_single_case(
            question, required_snippets, description
        )

        for i, missing in enumerate(all_missing, 1):
            if not missing:
                print(f"  Run {i}: ✓ all snippets present")
            else:
                print(f"  Run {i}: ✗ missing: {missing}")

        if all_passed:
            print(f"  Result: PASS ({success_count}/{RUNS_PER_TEST})")
            passed_cases += 1
        else:
            print(f"  Result: FAIL ({success_count}/{RUNS_PER_TEST})")

        print()

        total_runs += RUNS_PER_TEST
        total_successes += success_count

    # Summary
    print("=== Summary ===")
    print(f"Passed: {passed_cases}/{total_cases} test cases")
    consistency = (total_successes / total_runs) * 100 if total_runs > 0 else 0
    print(f"Overall consistency: {consistency:.1f}%")

    if passed_cases == total_cases:
        print("\nSUCCESS: All tests passed!")
    else:
        print(f"\nFAILED: {total_cases - passed_cases} test case(s) did not pass all runs.")


if __name__ == "__main__":
    run_all_tests()
