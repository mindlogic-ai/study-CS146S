import re

# Patterns that indicate urgency or priority
PRIORITY_KEYWORDS = {"urgent", "asap", "critical", "important", "blocker", "high-priority"}

# Prefixes that mark action items
ACTION_PREFIXES = re.compile(
    r"^(todo|action|fix|fixme|hack|bug|task|follow[\s-]?up|note)\s*[:]\s*",
    re.IGNORECASE,
)

# Patterns for checkbox-style items: [ ] or [x]
CHECKBOX_PATTERN = re.compile(r"^\[[\sx]\]\s*(.+)", re.IGNORECASE)

# Deadline patterns like "by Friday", "due 2024-01-01", "deadline: tomorrow"
DEADLINE_PATTERN = re.compile(
    r"(by\s+\w+|due\s+[\w\-/]+|deadline\s*:\s*\w+)",
    re.IGNORECASE,
)

# @mention pattern for assignments
MENTION_PATTERN = re.compile(r"@(\w+)")


def extract_action_items(text: str) -> list[dict]:
    """Extract action items from text with metadata (priority, assignee, deadline).

    Returns a list of dicts with keys: text, priority, assignee, has_deadline.
    """
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    results: list[dict] = []

    for line in lines:
        item = _try_extract(line)
        if item:
            results.append(item)

    return results


def _try_extract(line: str) -> dict | None:
    """Try to extract an action item from a single line."""
    normalized = line.lower()
    is_action = False

    # Check for action prefixes (TODO:, ACTION:, FIX:, etc.)
    if ACTION_PREFIXES.search(line):
        is_action = True

    # Check for checkbox-style items
    checkbox_match = CHECKBOX_PATTERN.match(line)
    if checkbox_match:
        is_action = True
        line = checkbox_match.group(1)

    # Check for exclamation emphasis
    if line.endswith("!"):
        is_action = True

    # Check for priority keywords anywhere in the line
    if any(kw in normalized for kw in PRIORITY_KEYWORDS):
        is_action = True

    if not is_action:
        return None

    # Extract metadata
    assignee = None
    mention = MENTION_PATTERN.search(line)
    if mention:
        assignee = mention.group(1)

    has_deadline = bool(DEADLINE_PATTERN.search(line))

    priority = "high" if any(kw in normalized for kw in PRIORITY_KEYWORDS) else "normal"

    return {
        "text": line,
        "priority": priority,
        "assignee": assignee,
        "has_deadline": has_deadline,
    }
