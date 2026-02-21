from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags_multiple():
    text = "Check #python and #fastapi"
    tags = extract_tags(text)
    assert tags == ["python", "fastapi"]


def test_extract_tags_none():
    text = "No tags here"
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_hyphenated():
    text = "Use #my-tag"
    tags = extract_tags(text)
    assert tags == ["my-tag"]


def test_extract_tags_numeric():
    text = "Week #2 stuff"
    tags = extract_tags(text)
    assert tags == ["2"]
