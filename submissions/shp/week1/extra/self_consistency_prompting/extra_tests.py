import os
import re
import sys
from collections import Counter
from typing import List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from self_consistency_prompting import YOUR_SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RUNS_PER_TEST = 5  # For majority voting

# (problem, expected_answer, description)
# Word problems that benefit from self-consistency (majority voting)
TEST_CASES: List[Tuple[str, int, str]] = [
    # Basic arithmetic word problems
    (
        "A store has 45 apples. They sell 18 apples in the morning and 12 in the afternoon. How many apples are left?",
        15,
        "basic subtraction",
    ),
    (
        "Tom has 3 boxes with 12 pencils each. He gives away 10 pencils. How many pencils does he have?",
        26,
        "multiplication then subtraction",
    ),
    # Multi-step problems
    (
        "A train travels 60 miles in the first hour and 80 miles in the second hour. What is the average speed in miles per hour?",
        70,
        "average calculation",
    ),
    (
        "Sarah has $50. She buys 3 books at $8 each. How much money does she have left?",
        26,
        "multiplication and subtraction",
    ),
    # Problems requiring careful reading
    (
        "A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?",
        9,
        "tricky wording",
    ),
    (
        "If you have 6 apples and you take away 4, how many do you have?",
        4,
        "tricky - you took them",
    ),
    # Rate/distance problems
    (
        "A car travels at 40 mph for 2 hours, then 60 mph for 3 hours. What is the total distance traveled?",
        260,
        "rate times time",
    ),
    # Percentage-like
    (
        "A pizza is cut into 8 slices. John eats 3 slices and Mary eats 2. How many slices are left?",
        3,
        "simple fractions",
    ),
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
) -> Tuple[bool, int, List[int | None], int | None]:
    """Test a single case with majority voting.

    Returns: (majority_correct, success_count, all_answers, majority_answer)
    """
    answers: List[int | None] = []

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

    # Count answers (excluding None)
    valid_answers = [a for a in answers if a is not None]
    if not valid_answers:
        return False, 0, answers, None

    counts = Counter(valid_answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    success_count = sum(1 for a in answers if a == expected)

    return majority_answer == expected, success_count, answers, majority_answer


def run_all_tests() -> None:
    """Run all test cases and print results."""
    print("=== Self-Consistency Prompting Extra Tests ===\n")

    total_cases = len(TEST_CASES)
    passed_cases = 0
    total_runs = 0
    total_successes = 0

    for problem, expected, description in TEST_CASES:
        # Truncate long problems for display
        display_problem = problem[:50] + "..." if len(problem) > 50 else problem
        print(f"Test: {display_problem}")
        print(f"  Expected: {expected} ({description})")

        majority_correct, success_count, answers, majority_answer = test_single_case(
            problem, expected, description
        )

        for i, answer in enumerate(answers, 1):
            if answer == expected:
                print(f"  Run {i}: ✓ {answer}")
            else:
                print(f"  Run {i}: ✗ {answer}")

        print(f"  Majority answer: {majority_answer}")

        if majority_correct:
            print(f"  Result: PASS (majority={majority_answer}, {success_count}/{RUNS_PER_TEST} correct)")
            passed_cases += 1
        else:
            print(f"  Result: FAIL (majority={majority_answer}, expected={expected})")

        print()

        total_runs += RUNS_PER_TEST
        total_successes += success_count

    # Summary
    print("=== Summary ===")
    print(f"Passed: {passed_cases}/{total_cases} test cases (majority voting)")
    consistency = (total_successes / total_runs) * 100 if total_runs > 0 else 0
    print(f"Overall consistency: {consistency:.1f}%")

    if passed_cases == total_cases:
        print("\nSUCCESS: All tests passed!")
    else:
        print(f"\nFAILED: {total_cases - passed_cases} test case(s) had wrong majority answer.")


if __name__ == "__main__":
    run_all_tests()
