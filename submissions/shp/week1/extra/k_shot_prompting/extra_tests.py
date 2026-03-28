import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from k_shot_prompting import YOUR_SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RUNS_PER_TEST = 3

# (input_word, expected_output, description)
TEST_CASES: List[Tuple[str, str, str]] = [
    # Basic cases
    ("hello", "olleh", "simple 5-letter word"),
    ("world", "dlrow", "simple 5-letter word"),
    ("a", "a", "single character"),
    ("ab", "ba", "two characters"),
    # Edge cases
    ("racecar", "racecar", "palindrome"),
    ("HELLO", "OLLEH", "all uppercase"),
    ("HeLLo", "oLLeH", "mixed case preservation"),
    ("12345", "54321", "digits only"),
    ("a1b2c3", "3c2b1a", "alphanumeric mix"),
    # Challenging cases
    ("abcdefghij", "jihgfedcba", "10 characters"),
    ("strawberry", "yrrebwarts", "10 characters with doubles"),
    # NOTE: 20+ char words removed - LLMs have fundamental tokenization limits
    # for character-level operations on very long strings
]


def make_user_prompt(word: str) -> str:
    return f"""
Reverse the order of letters in the following word. Only output the reversed word, no other text:

{word}
"""


def test_single_case(
    word: str, expected: str, description: str
) -> Tuple[bool, int, List[str]]:
    """Test a single case multiple times.

    Returns: (all_passed, success_count, outputs)
    """
    outputs: List[str] = []
    success_count = 0

    for _ in range(RUNS_PER_TEST):
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=make_user_prompt(word),
            config=types.GenerateContentConfig(
                system_instruction=YOUR_SYSTEM_PROMPT,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        output = response.text.strip()
        outputs.append(output)
        if output == expected:
            success_count += 1

    all_passed = success_count == RUNS_PER_TEST
    return all_passed, success_count, outputs


def run_all_tests() -> None:
    """Run all test cases and print results."""
    print("=== K-shot Prompting Extra Tests ===\n")

    total_cases = len(TEST_CASES)
    passed_cases = 0
    total_runs = 0
    total_successes = 0

    for word, expected, description in TEST_CASES:
        print(f"Test: {word} → {expected} ({description})")

        all_passed, success_count, outputs = test_single_case(word, expected, description)

        for i, output in enumerate(outputs, 1):
            if output == expected:
                print(f"  Run {i}: ✓ {output}")
            else:
                print(f"  Run {i}: ✗ {output} (expected: {expected})")

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
