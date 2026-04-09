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


def test_extract_tags_basic():
    text = "Fix the #bug in the login page #urgent"
    tags = extract_tags(text)
    assert "bug" in tags
    assert "urgent" in tags
    assert len(tags) == 2


def test_extract_tags_deduplication():
    text = "#bug found again #bug still broken #feature"
    tags = extract_tags(text)
    assert tags.count("bug") == 1
    assert "feature" in tags
    assert len(tags) == 2


def test_extract_tags_empty():
    text = "No tags here, just plain text."
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_multiline():
    text = """Line one #backend
    Line two #frontend
    Line three #backend #api"""
    tags = extract_tags(text)
    assert "backend" in tags
    assert "frontend" in tags
    assert "api" in tags
    assert tags.count("backend") == 1
