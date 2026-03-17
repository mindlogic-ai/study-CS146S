import re
from typing import TypedDict


class ActionItem(TypedDict):
    text: str
    priority: str
    deadline: str | None
    category: str | None


HIGH_PRIORITY_KEYWORDS = {"urgent", "asap", "critical", "immediately", "emergency", "blocking"}
MEDIUM_PRIORITY_KEYWORDS = {"important", "soon", "needed", "should", "priority"}
LOW_PRIORITY_KEYWORDS = {"low", "eventually", "someday", "backlog", "nice to have", "optional"}

CATEGORY_PATTERNS: dict[str, list[str]] = {
    "bug": [r"\bbug\b", r"\bfix\b", r"\bbroken\b", r"\berror\b", r"\bissue\b", r"\bcrash\b",
            r"\bdefect\b", r"\bpatch\b"],
    "feature": [r"\bfeature\b", r"\badd\b", r"\bimplement\b", r"\bcreate\b", r"\bbuild\b",
                r"\bnew\b"],
    "review": [r"\breview\b", r"\bPR\b", r"\bfeedback\b", r"\bapprove\b", r"\bcheck\b"],
    "deploy": [r"\bdeploy\b", r"\brelease\b", r"\bship\b", r"\blaunch\b", r"\bpublish\b",
               r"\brollout\b", r"\bproduction\b"],
}

# Patterns for deadline extraction
DEADLINE_PATTERNS = [
    # "due 2024-03-15" or "by 2024-03-15"
    r"(?:due|by|before|until)\s+(\d{4}-\d{2}-\d{2})",
    # "by Friday", "by Monday", etc.
    r"(?:due|by|before|until)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",
    # "by March 15" or "before March"
    r"(?:due|by|before|until)\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"(?:\s+\d{1,2})?",
    # "due next week", "by end of day", "by EOD", "by tomorrow"
    r"(?:due|by|before|until)\s+(next\s+\w+|end\s+of\s+\w+|EOD|tomorrow|today)",
]


def _detect_priority(text: str) -> str:
    lower = text.lower()
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in lower:
            return "high"
    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in lower:
            return "medium"
    for keyword in LOW_PRIORITY_KEYWORDS:
        if keyword in lower:
            return "low"
    return "medium"


def _extract_deadline(text: str) -> str | None:
    lower = text.lower()
    for pattern in DEADLINE_PATTERNS:
        match = re.search(pattern, lower if "Monday" not in pattern else text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _detect_category(text: str) -> str | None:
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return category
    return None


def extract_action_items(text: str) -> list[ActionItem]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[ActionItem] = []
    for line in lines:
        normalized = line.lower()
        is_action = False
        if normalized.startswith("todo:") or normalized.startswith("action:"):
            is_action = True
        elif line.endswith("!"):
            is_action = True

        if is_action:
            results.append(
                ActionItem(
                    text=line,
                    priority=_detect_priority(line),
                    deadline=_extract_deadline(line),
                    category=_detect_category(line),
                )
            )
    return results
