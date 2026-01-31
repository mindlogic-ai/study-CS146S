import os
import re
import sys
from typing import Callable, List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reflexion import YOUR_REFLEXION_PROMPT, your_build_reflexion_context

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Different validation tasks for reflexion testing
# (task_name, system_prompt, test_cases, description)
VALIDATION_TASKS: List[Tuple[str, str, List[Tuple[str, bool]], str]] = [
    (
        "is_valid_email",
        """You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_valid_email(email: str) -> bool. No prose or comments.
The function should validate email format (contains @, has domain after @, has local part before @).""",
        [
            ("test@example.com", True),
            ("user.name@domain.org", True),
            ("invalid", False),
            ("@nodomain.com", False),
            ("noatsign.com", False),
            ("missing@", False),
        ],
        "email validation",
    ),
    (
        "is_valid_phone",
        """You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_valid_phone(phone: str) -> bool. No prose or comments.
The function should validate US phone numbers: exactly 10 digits, optionally with dashes (e.g., 123-456-7890 or 1234567890).""",
        [
            ("1234567890", True),
            ("123-456-7890", True),
            ("123456789", False),  # 9 digits
            ("12345678901", False),  # 11 digits
            ("123-45-67890", False),  # wrong dash placement
            ("abc-def-ghij", False),  # letters
        ],
        "phone validation",
    ),
    (
        "is_palindrome",
        """You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_palindrome(s: str) -> bool. No prose or comments.
The function should check if a string is a palindrome (reads same forwards and backwards), ignoring case and non-alphanumeric characters.""",
        [
            ("racecar", True),
            ("A man a plan a canal Panama", True),
            ("hello", False),
            ("Was it a car or a cat I saw?", True),
            ("No lemon, no melon", True),
            ("not a palindrome", False),
        ],
        "palindrome check",
    ),
]


def extract_code_block(text: str) -> str:
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()


def load_function_from_code(code_str: str, func_name: str) -> Callable:
    namespace: dict = {}
    exec(code_str, namespace)
    func = namespace.get(func_name)
    if not callable(func):
        raise ValueError(f"No callable {func_name} found in generated code")
    return func


def evaluate_function(
    func: Callable, test_cases: List[Tuple[str, bool]]
) -> Tuple[bool, List[str]]:
    failures: List[str] = []
    for input_val, expected in test_cases:
        try:
            result = bool(func(input_val))
        except Exception as exc:
            failures.append(f"Input: {input_val} → raised exception: {exc}")
            continue

        if result != expected:
            failures.append(f"Input: {input_val} → expected {expected}, got {result}")

    return (len(failures) == 0, failures)


def generate_initial_function(system_prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Provide the implementation now.",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=1.0,
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.MINIMAL
            ),
        ),
    )
    return extract_code_block(response.text)


def apply_reflexion(prev_code: str, failures: List[str]) -> str:
    reflection_context = your_build_reflexion_context(prev_code, failures)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=reflection_context,
        config=types.GenerateContentConfig(
            system_instruction=YOUR_REFLEXION_PROMPT,
            temperature=1.0,
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.MINIMAL
            ),
        ),
    )
    return extract_code_block(response.text)


def run_single_task(
    func_name: str,
    system_prompt: str,
    test_cases: List[Tuple[str, bool]],
    description: str,
) -> Tuple[bool, str]:
    """Run reflexion flow for a single task.

    Returns: (passed, stage_passed_at)
    """
    # 1) Generate initial function
    try:
        initial_code = generate_initial_function(system_prompt)
        func = load_function_from_code(initial_code, func_name)
        passed, failures = evaluate_function(func, test_cases)

        if passed:
            return True, "initial"
    except Exception as exc:
        failures = [f"Code generation/loading failed: {exc}"]
        initial_code = ""

    # 2) Apply reflexion
    try:
        improved_code = apply_reflexion(initial_code, failures)
        improved_func = load_function_from_code(improved_code, func_name)
        passed2, failures2 = evaluate_function(improved_func, test_cases)

        if passed2:
            return True, "reflexion"
    except Exception as exc:
        pass

    return False, "failed"


def run_all_tests() -> None:
    """Run all validation tasks and print results."""
    print("=== Reflexion Extra Tests ===\n")

    total_tasks = len(VALIDATION_TASKS)
    passed_tasks = 0
    initial_passes = 0
    reflexion_passes = 0

    for func_name, system_prompt, test_cases, description in VALIDATION_TASKS:
        print(f"Test: {func_name} ({description})")
        print(f"  Test cases: {len(test_cases)}")

        passed, stage = run_single_task(func_name, system_prompt, test_cases, description)

        if passed:
            if stage == "initial":
                print(f"  Result: PASS (initial implementation worked)")
                initial_passes += 1
            else:
                print(f"  Result: PASS (fixed after reflexion)")
                reflexion_passes += 1
            passed_tasks += 1
        else:
            print(f"  Result: FAIL (still failing after reflexion)")

        print()

    # Summary
    print("=== Summary ===")
    print(f"Passed: {passed_tasks}/{total_tasks} tasks")
    print(f"  - Initial pass: {initial_passes}")
    print(f"  - After reflexion: {reflexion_passes}")
    print(f"  - Failed: {total_tasks - passed_tasks}")

    if passed_tasks == total_tasks:
        print("\nSUCCESS: All tests passed!")
    else:
        print(f"\nFAILED: {total_tasks - passed_tasks} task(s) could not be fixed.")


if __name__ == "__main__":
    run_all_tests()
