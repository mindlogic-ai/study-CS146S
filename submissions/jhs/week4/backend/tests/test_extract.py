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
    assert len(items) == 2


def test_extract_action_items_empty():
    assert extract_action_items("") == []


def test_extract_action_items_no_matches():
    assert extract_action_items("Just a regular note\nwith no actions") == []


def test_extract_tags():
    text = "Check #urgent and #backend tasks. Also #urgent again."
    tags = extract_tags(text)
    assert tags == ["backend", "urgent"]


def test_extract_tags_empty():
    assert extract_tags("No tags here") == []


def test_extract_tags_single():
    assert extract_tags("Only #one tag") == ["one"]
