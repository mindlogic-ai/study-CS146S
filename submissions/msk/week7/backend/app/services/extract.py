import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedItem:
    text: str
    category: str = "general"
    priority: str = "normal"


_PRIORITY_PATTERN = re.compile(r"\[(?:P0|URGENT)\]", re.IGNORECASE)
_HIGH_PATTERN = re.compile(r"\[(?:P1|HIGH)\]", re.IGNORECASE)
_DEADLINE_PATTERN = re.compile(r"(?:by EOD|due\s+\S+)", re.IGNORECASE)
_CHECKBOX_PATTERN = re.compile(r"^\[[ ]\]")


def _detect_priority(line: str) -> str:
    if _PRIORITY_PATTERN.search(line):
        return "urgent"
    if _HIGH_PATTERN.search(line):
        return "high"
    return "normal"


def extract_action_items(text: str) -> list[str]:
    """Legacy interface: returns plain strings."""
    return [item.text for item in extract_action_items_detailed(text)]


def extract_action_items_detailed(text: str) -> list[ExtractedItem]:
    results: list[ExtractedItem] = []
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("- ")
        if not line:
            continue

        normalized = line.lower()
        priority = _detect_priority(line)

        if normalized.startswith("todo:") or normalized.startswith("action:"):
            results.append(ExtractedItem(text=line, category="action", priority=priority))
        elif normalized.startswith(("fixme:", "hack:", "bug:")):
            results.append(ExtractedItem(text=line, category="bug", priority=priority))
        elif normalized.startswith("note:"):
            results.append(ExtractedItem(text=line, category="note", priority=priority))
        elif normalized.startswith("@todo"):
            results.append(ExtractedItem(text=line, category="action", priority=priority))
        elif _CHECKBOX_PATTERN.match(line):
            item_text = line[3:].strip()
            results.append(
                ExtractedItem(text=item_text or line, category="task", priority=priority)
            )
        elif line.endswith("!"):
            results.append(ExtractedItem(text=line, category="general", priority=priority))

        if _DEADLINE_PATTERN.search(line) and results and results[-1].text in (
            line,
            line[3:].strip(),
        ):
            last = results[-1]
            results[-1] = ExtractedItem(
                text=last.text,
                category=last.category,
                priority="high" if last.priority == "normal" else last.priority,
            )

    return results
