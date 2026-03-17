from backend.app.services.extract import extract_action_items


def test_extract_basic_prefixes():
    text = "TODO: write tests\nACTION: review PR\nJust a comment"
    items = extract_action_items(text)
    texts = [i["text"] for i in items]
    assert "TODO: write tests" in texts
    assert "ACTION: review PR" in texts
    assert "Just a comment" not in texts


def test_extract_exclamation():
    text = "Ship it!\nNot actionable"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["text"] == "Ship it!"


def test_extract_checkbox():
    text = "[ ] Buy groceries\n[x] Already done\nPlain line"
    items = extract_action_items(text)
    texts = [i["text"] for i in items]
    assert "Buy groceries" in texts
    assert "Already done" in texts
    assert len(items) == 2


def test_extract_priority_keywords():
    text = "This is urgent fix the server\nNormal line"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["priority"] == "high"


def test_extract_assignee():
    text = "TODO: @alice fix the login bug"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["assignee"] == "alice"


def test_extract_deadline():
    text = "TODO: deploy by Friday"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["has_deadline"] is True


def test_extract_additional_prefixes():
    text = "FIX: memory leak\nBUG: crash on startup\nfollow-up: check metrics"
    items = extract_action_items(text)
    texts = [i["text"] for i in items]
    assert "FIX: memory leak" in texts
    assert "BUG: crash on startup" in texts
    assert "follow-up: check metrics" in texts


def test_extract_empty_text():
    assert extract_action_items("") == []
    assert extract_action_items("   \n\n  ") == []
