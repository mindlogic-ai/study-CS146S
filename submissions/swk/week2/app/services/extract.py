from __future__ import annotations

import os
import re
from typing import Any, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


# -----------------------------------------------------------------------------
# LLM-powered extraction using Google Gemini API
# -----------------------------------------------------------------------------

def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using Google Gemini API.

    Uses structured output to return a JSON array of action item strings.
    Falls back to empty list if extraction fails or input is empty.

    Args:
        text: Free-form text containing potential action items

    Returns:
        List of extracted action item strings
    """
    if not text or not text.strip():
        return []

    prompt = f"""You are an action item extractor. Analyze the following text and extract all action items, tasks, or to-dos.

Rules:
- Extract clear, actionable items only
- Each item should be a concise task description
- Remove bullet points, checkboxes, or numbering from the output
- If no action items are found, return an empty array
- Return items in the order they appear in the text

Text to analyze:
\"\"\"
{text}
\"\"\"

Return ONLY a JSON array of strings, no other text. Example: ["Task 1", "Task 2"]"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "array",
                    "items": {"type": "string"}
                },
                temperature=0.1,  # Low temperature for consistent extraction
            ),
        )

        # Parse the JSON response
        import json
        result = json.loads(response.text)

        if isinstance(result, list):
            # Filter out empty strings and deduplicate
            seen: set[str] = set()
            unique: List[str] = []
            for item in result:
                if isinstance(item, str) and item.strip():
                    lowered = item.strip().lower()
                    if lowered not in seen:
                        seen.add(lowered)
                        unique.append(item.strip())
            return unique
        return []

    except Exception as e:
        # Log error and return empty list on failure
        print(f"Error in LLM extraction: {e}")
        return []
