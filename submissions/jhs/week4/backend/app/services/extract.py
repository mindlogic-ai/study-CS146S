import re


def extract_action_items(text: str) -> list[str]:
    """Extract actionable items from text.

    Identifies lines ending with '!' or starting with 'TODO:'.
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Extract #hashtag-style tags from text."""
    return sorted(set(re.findall(r"#(\w+)", text)))
