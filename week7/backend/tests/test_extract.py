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
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_fixme_and_hack():
    text = "FIXME: broken alignment\nHACK: temporary workaround"
    items = extract_action_items(text)
    assert "FIXME: broken alignment" in items
    assert "HACK: temporary workaround" in items


def test_extract_follow_up():
    items = extract_action_items("Follow-up: circle back with PM")
    assert len(items) == 1
    assert "Follow-up: circle back with PM" in items


def test_extract_imperative_keywords():
    text = "Need to update the docs\nShould refactor the parser\nMust deploy by Friday"
    items = extract_action_items(text)
    assert len(items) == 3


def test_extract_deadline_mentions():
    text = "Review slides by Friday\nSubmit report before 3/15\nDue tomorrow"
    items = extract_action_items(text)
    assert len(items) == 3


def test_extract_checkbox_items():
    text = "- [ ] Write unit tests\n- [x] Setup CI\n- [ ] Deploy to staging"
    items = extract_action_items(text)
    assert "Write unit tests" in items
    assert "Setup CI" in items
    assert "Deploy to staging" in items


def test_extract_mention_pattern():
    items = extract_action_items("Assign to [@alice] for review")
    assert len(items) == 1


def test_no_duplicates():
    text = "TODO: write tests\nTODO: write tests"
    items = extract_action_items(text)
    assert len(items) == 1


def test_non_actionable_lines_ignored():
    text = "Just a regular note\nNothing to do here\nAll good"
    items = extract_action_items(text)
    assert len(items) == 0
