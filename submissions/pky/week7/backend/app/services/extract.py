import re
from dataclasses import dataclass, field


@dataclass
class ExtractedItem:
    text: str
    priority: str = "medium"
    deadline: str | None = None
    assignees: list[str] = field(default_factory=list)


_KEYWORDS = ("todo:", "action:", "fixme:", "task:", "bug:", "follow-up:", "reminder:")


def _detect_priority(text: str) -> str:
    if re.search(r"\b(urgent|critical|asap)\b", text, re.IGNORECASE):
        return "high"
    if re.search(r"\b(nice to have|eventually|low priority)\b", text, re.IGNORECASE):
        return "low"
    return "medium"


def _parse_deadline(text: str) -> str | None:
    m = re.search(r"\b(?:by|due)\s+(\S+(?:\s+\S+)?)", text, re.IGNORECASE)
    return m.group(1) if m else None


def _parse_assignees(text: str) -> list[str]:
    return re.findall(r"@(\w+)", text)


def extract_action_items(text: str) -> list[ExtractedItem]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[ExtractedItem] = []
    for line in lines:
        normalized = line.lower()
        matched = any(normalized.startswith(kw) for kw in _KEYWORDS) or line.endswith("!")
        if matched:
            results.append(
                ExtractedItem(
                    text=line,
                    priority=_detect_priority(line),
                    deadline=_parse_deadline(line),
                    assignees=_parse_assignees(line),
                )
            )
    return results
