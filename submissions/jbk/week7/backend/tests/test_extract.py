from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    texts = [item["text"] for item in items]
    assert "TODO: write tests" in texts
    assert "ACTION: review PR" in texts
    assert "Ship it!" in texts
    # All items should have the required keys
    for item in items:
        assert "text" in item
        assert "priority" in item
        assert "deadline" in item
        assert "category" in item


def test_priority_detection_high():
    text = "- TODO: urgent fix the login bug asap"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["priority"] == "high"


def test_priority_detection_medium():
    text = "- TODO: important update the docs"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["priority"] == "medium"


def test_priority_detection_low():
    text = "- TODO: eventually clean up old logs"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["priority"] == "low"


def test_priority_default_medium():
    text = "- TODO: write tests"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["priority"] == "medium"


def test_deadline_date_format():
    text = "- TODO: submit report by 2024-03-15"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["deadline"] == "2024-03-15"


def test_deadline_by_day():
    text = "- TODO: finish review by Friday"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["deadline"] == "Friday"


def test_deadline_before_month():
    text = "- TODO: deploy before March"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["deadline"] == "march"


def test_deadline_due_date():
    text = "- ACTION: release due 2024-06-01"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["deadline"] == "2024-06-01"


def test_deadline_none():
    text = "- TODO: write tests"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["deadline"] is None


def test_category_bug():
    text = "- TODO: fix the login bug"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["category"] == "bug"


def test_category_feature():
    text = "- TODO: add new search feature"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["category"] == "feature"


def test_category_review():
    text = "- ACTION: review PR #42"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["category"] == "review"


def test_category_deploy():
    text = "- TODO: deploy to production"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["category"] == "deploy"


def test_category_none():
    text = "- TODO: update the README"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["category"] is None


def test_combined_extraction():
    text = "- TODO: urgent fix critical bug by Friday"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["text"] == "TODO: urgent fix critical bug by Friday"
    assert items[0]["priority"] == "high"
    assert items[0]["deadline"] == "Friday"
    assert items[0]["category"] == "bug"


def test_exclamation_action():
    text = "- Ship it!"
    items = extract_action_items(text)
    assert len(items) == 1
    assert items[0]["text"] == "Ship it!"
    assert items[0]["category"] == "deploy"


def test_non_actionable_skipped():
    text = "This is just a regular note"
    items = extract_action_items(text)
    assert len(items) == 0


def test_multiple_items_mixed():
    text = """
    - TODO: urgent deploy by 2024-03-15
    - ACTION: review PR feedback
    - Regular note
    - Fix the crash!
    - TODO: eventually add nice to have backlog item
    """.strip()
    items = extract_action_items(text)
    assert len(items) == 4

    assert items[0]["priority"] == "high"
    assert items[0]["deadline"] == "2024-03-15"
    assert items[0]["category"] == "deploy"

    assert items[1]["category"] == "review"

    assert items[2]["text"] == "Fix the crash!"
    assert items[2]["category"] == "bug"

    assert items[3]["priority"] == "low"
