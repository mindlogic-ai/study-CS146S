from backend.app.services.extract import ExtractedItem, extract_action_items


def test_keyword_todo():
    items = extract_action_items("TODO: write tests")
    assert len(items) == 1
    assert items[0].text == "TODO: write tests"


def test_keyword_action():
    items = extract_action_items("ACTION: review PR")
    assert len(items) == 1
    assert items[0].text == "ACTION: review PR"


def test_keyword_fixme():
    items = extract_action_items("FIXME: broken layout")
    assert len(items) == 1
    assert items[0].text == "FIXME: broken layout"


def test_keyword_task():
    items = extract_action_items("TASK: deploy to staging")
    assert len(items) == 1


def test_keyword_bug():
    items = extract_action_items("BUG: login fails on Safari")
    assert len(items) == 1


def test_exclamation_rule():
    items = extract_action_items("Ship it!")
    assert len(items) == 1
    assert items[0].text == "Ship it!"


def test_priority_high():
    items = extract_action_items("TODO: fix this URGENT issue")
    assert items[0].priority == "high"

    items = extract_action_items("TODO: critical bug")
    assert items[0].priority == "high"

    items = extract_action_items("TODO: do this ASAP")
    assert items[0].priority == "high"


def test_priority_low():
    items = extract_action_items("TODO: nice to have feature")
    assert items[0].priority == "low"

    items = extract_action_items("TODO: eventually refactor this")
    assert items[0].priority == "low"

    items = extract_action_items("TODO: low priority cleanup")
    assert items[0].priority == "low"


def test_priority_medium_default():
    items = extract_action_items("TODO: write docs")
    assert items[0].priority == "medium"


def test_deadline_by():
    items = extract_action_items("TODO: finish by Friday")
    assert items[0].deadline == "Friday"


def test_deadline_due():
    items = extract_action_items("TODO: due 2024-01-15 submit report")
    assert items[0].deadline == "2024-01-15 submit"


def test_deadline_none():
    items = extract_action_items("TODO: write tests")
    assert items[0].deadline is None


def test_assignee_single():
    items = extract_action_items("TODO: @alice review this")
    assert items[0].assignees == ["alice"]


def test_assignee_multiple():
    items = extract_action_items("TODO: @alice and @bob pair on this")
    assert items[0].assignees == ["alice", "bob"]


def test_no_assignees():
    items = extract_action_items("TODO: write tests")
    assert items[0].assignees == []


def test_empty_text():
    items = extract_action_items("")
    assert items == []


def test_no_matches():
    items = extract_action_items("This is just a regular note\nWith no action items")
    assert items == []


def test_combined_extraction():
    text = """
    TODO: urgent fix by Friday @alice
    ACTION: nice to have cleanup
    Regular line
    Ship it!
    """.strip()
    items = extract_action_items(text)
    assert len(items) == 3

    assert items[0].text == "TODO: urgent fix by Friday @alice"
    assert items[0].priority == "high"
    assert items[0].deadline == "Friday @alice"
    assert items[0].assignees == ["alice"]

    assert items[1].text == "ACTION: nice to have cleanup"
    assert items[1].priority == "low"

    assert items[2].text == "Ship it!"
    assert items[2].priority == "medium"


def test_returns_extracted_item_dataclass():
    items = extract_action_items("TODO: test")
    assert isinstance(items[0], ExtractedItem)
