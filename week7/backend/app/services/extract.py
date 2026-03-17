import re


_KEYWORD_PATTERNS = [
    re.compile(r"^(TODO|FIXME|HACK|ACTION|FOLLOW[\s-]?UP)\s*:", re.IGNORECASE),
    re.compile(r"^(need|must|should|have to|please)\s+\w+", re.IGNORECASE),
    re.compile(r"\[@\w+\]"),  # mentions like [@alice]
    re.compile(
        r"\b(by|before|due|deadline)\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        r"|tomorrow|end of (day|week)|eod|eow"
        r"|\d{1,2}/\d{1,2})",
        re.IGNORECASE,
    ),
]

_CHECKBOX_RE = re.compile(r"^\s*(?:[-*]\s*)?\[[ xX]?\]\s*(.+)")


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[str] = []
    seen: set[str] = set()

    for line in lines:
        normalized = line.lower()
        matched = False

        # Original patterns: TODO:/ACTION: prefix or trailing !
        if normalized.startswith("todo:") or normalized.startswith("action:"):
            matched = True
        elif line.endswith("!"):
            matched = True

        # Checkbox items: - [ ] or - [x]
        if not matched:
            cb = _CHECKBOX_RE.match(line)
            if cb:
                line = cb.group(1).strip()
                matched = True

        # Keyword / regex patterns
        if not matched:
            for pat in _KEYWORD_PATTERNS:
                if pat.search(line):
                    matched = True
                    break

        if matched and line not in seen:
            seen.add(line)
            results.append(line)

    return results
