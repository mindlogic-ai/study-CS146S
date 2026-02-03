import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

NUM_RUNS_TIMES = 5

YOUR_SYSTEM_PROMPT = """You are a letter reversal expert. You reverse the order of letters in words.

Examples:
Input: hello
Output: olleh

Input: world
Output: dlrow

Input: python
Output: nohtyp

Input: abc
Output: cba

Input: testing
Output: gnitset

Now reverse the letters in the given word. Output ONLY the reversed word, nothing else."""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=USER_PROMPT,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=1.0,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
        output_text = response.text.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
