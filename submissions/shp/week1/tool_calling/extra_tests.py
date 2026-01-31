import json
import os
import sys
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tool_calling import YOUR_SYSTEM_PROMPT, TOOL_REGISTRY, execute_tool_call

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RUNS_PER_TEST = 3

# (user_message, expected_tool, description)
TEST_CASES: List[Tuple[str, str, str]] = [
    ("Call the tool now.", "output_every_func_return_type", "direct command"),
    ("Please invoke the available tool.", "output_every_func_return_type", "polite request"),
    ("Use the tool to list function return types.", "output_every_func_return_type", "descriptive"),
    ("Execute the function analysis tool.", "output_every_func_return_type", "different wording"),
    ("I need to see the return types. Call the tool.", "output_every_func_return_type", "with context"),
]


def extract_tool_call(text: str) -> Dict[str, Any] | None:
    """Parse a JSON object from the model output."""
    text = text.strip()
    # Strip code fences if present
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json\n"):
            text = text[5:]
        elif text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        obj = json.loads(text)
        return obj
    except json.JSONDecodeError:
        return None


def validate_tool_call(call: Dict[str, Any] | None, expected_tool: str) -> Tuple[bool, str]:
    """Validate that the tool call is correct.

    Returns: (is_valid, error_message)
    """
    if call is None:
        return False, "Failed to parse JSON"

    if "tool" not in call:
        return False, "Missing 'tool' key"

    if call["tool"] != expected_tool:
        return False, f"Wrong tool: {call['tool']}"

    if "args" not in call:
        return False, "Missing 'args' key"

    if not isinstance(call["args"], dict):
        return False, f"'args' is not an object: {type(call['args'])}"

    # Try to execute the tool call
    try:
        execute_tool_call(call)
    except Exception as exc:
        return False, f"Tool execution failed: {exc}"

    return True, "OK"


def test_single_case(
    user_message: str, expected_tool: str, description: str
) -> Tuple[bool, int, List[str]]:
    """Test a single case multiple times.

    Returns: (all_passed, success_count, results)
    """
    results: List[str] = []
    success_count = 0

    for _ in range(RUNS_PER_TEST):
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=YOUR_SYSTEM_PROMPT,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        output = response.text.strip()
        call = extract_tool_call(output)
        is_valid, error = validate_tool_call(call, expected_tool)

        if is_valid:
            results.append("valid JSON, correct tool")
            success_count += 1
        else:
            results.append(error)

    all_passed = success_count == RUNS_PER_TEST
    return all_passed, success_count, results


def run_all_tests() -> None:
    """Run all test cases and print results."""
    print("=== Tool Calling Extra Tests ===\n")

    total_cases = len(TEST_CASES)
    passed_cases = 0
    total_runs = 0
    total_successes = 0

    for user_message, expected_tool, description in TEST_CASES:
        display_msg = user_message[:40] + "..." if len(user_message) > 40 else user_message
        print(f"Test: \"{display_msg}\" ({description})")

        all_passed, success_count, results = test_single_case(
            user_message, expected_tool, description
        )

        for i, result in enumerate(results, 1):
            if "valid" in result.lower():
                print(f"  Run {i}: ✓ {result}")
            else:
                print(f"  Run {i}: ✗ {result}")

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
