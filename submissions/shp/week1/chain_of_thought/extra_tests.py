import os
import re
import sys
from typing import List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chain_of_thought import YOUR_SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RUNS_PER_TEST = 3

# (problem, expected_answer, description)
# These are modular exponentiation problems that require step-by-step reasoning
TEST_CASES: List[Tuple[str, int, str]] = [
    # Basic cases
    ("what is 2^10 (mod 100)?", 24, "simple power of 2"),
    ("what is 3^4 (mod 10)?", 1, "small exponent"),
    ("what is 7^2 (mod 5)?", 4, "very small"),
    # Medium cases
    ("what is 2^100 (mod 100)?", 76, "large exponent, pattern needed"),
    ("what is 5^13 (mod 7)?", 5, "Fermat's little theorem applicable"),
    # Challenging cases
    ("what is 3^1000 (mod 100)?", 1, "very large exponent"),
    ("what is 17^23 (mod 100)?", 77, "larger base"),
    # Edge cases
    ("what is 1^999 (mod 50)?", 1, "base is 1"),
    ("what is 10^5 (mod 100)?", 0, "result is 0"),
]


def make_user_prompt(problem: str) -> str:
    return f"""
Solve this problem, then give the final answer on the last line as "Answer: <number>".

{problem}
"""


def extract_final_answer(text: str) -> int | None:
    """Extract the numeric answer from the response."""
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return int(float(num_match.group(0)))
    return None


def test_single_case(
    problem: str, expected: int, description: str
) -> Tuple[bool, int, List[int | None]]:
    """Test a single case multiple times.

    Returns: (all_passed, success_count, answers)
    """
    answers: List[int | None] = []
    success_count = 0

    for _ in range(RUNS_PER_TEST):
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=make_user_prompt(problem),
            config=types.GenerateContentConfig(
                system_instruction=YOUR_SYSTEM_PROMPT,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        answer = extract_final_answer(response.text)
        answers.append(answer)
        if answer == expected:
            success_count += 1

    all_passed = success_count == RUNS_PER_TEST
    return all_passed, success_count, answers


def run_all_tests() -> None:
    """Run all test cases and print results."""
    print("=== Chain of Thought Extra Tests ===\n")

    total_cases = len(TEST_CASES)
    passed_cases = 0
    total_runs = 0
    total_successes = 0

    for problem, expected, description in TEST_CASES:
        print(f"Test: {problem} → {expected} ({description})")

        all_passed, success_count, answers = test_single_case(problem, expected, description)

        for i, answer in enumerate(answers, 1):
            if answer == expected:
                print(f"  Run {i}: ✓ {answer}")
            else:
                print(f"  Run {i}: ✗ {answer} (expected: {expected})")

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
