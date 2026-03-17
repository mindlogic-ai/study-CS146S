import re
from dataclasses import dataclass

KEYWORDS = ("todo:", "action:", "fixme:", "bug:", "hack:", "task:", "follow-up:", "reminder:")

HIGH_PATTERNS = re.compile(r"\burgent\b|\bcritical\b|\basap\b|\bimmediately\b|\[p0\]|\[high\]", re.I)
LOW_PATTERNS = re.compile(r"\bnice to have\b|\beventually\b|\blow priority\b|\[p2\]|\[low\]", re.I)

DEADLINE_PATTERN = re.compile(r"\b(?:by|due|before|deadline)\s+(.+?)(?:\s*$)", re.I)

CATEGORY_BUG = re.compile(r"\bbug\b|\bfix", re.I)
CATEGORY_REVIEW = re.compile(r"\breview\b|\bPR\b", re.I)
CATEGORY_FEATURE = re.compile(r"\bfeature\b|\bimplement\b|\badd\b", re.I)


@dataclass
class ExtractedItem:
    text: str
    priority: str  # high, medium, low
    deadline: str | None
    category: str  # bug, review, feature, task


def _detect_priority(text: str) -> str:
    if HIGH_PATTERNS.search(text):
        return "high"
    if LOW_PATTERNS.search(text):
        return "low"
    return "medium"


def _detect_deadline(text: str) -> str | None:
    m = DEADLINE_PATTERN.search(text)
    if m:
        return m.group(1).strip()
    return None


def _detect_category(text: str) -> str:
    normalized = text.lower()
    if normalized.startswith("bug:") or normalized.startswith("fixme:") or CATEGORY_BUG.search(text):
        return "bug"
    if CATEGORY_REVIEW.search(text):
        return "review"
    if CATEGORY_FEATURE.search(text):
        return "feature"
    return "task"


def extract_action_items(text: str) -> list[ExtractedItem]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[ExtractedItem] = []
    for line in lines:
        normalized = line.lower()
        is_match = any(normalized.startswith(kw) for kw in KEYWORDS) or line.endswith("!")
        if is_match:
            results.append(
                ExtractedItem(
                    text=line,
                    priority=_detect_priority(line),
                    deadline=_detect_deadline(line),
                    category=_detect_category(line),
                )
            )
    return results
