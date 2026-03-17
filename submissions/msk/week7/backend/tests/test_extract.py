from backend.app.services.extract import extract_action_items, extract_action_items_detailed


def test_extract_action_items_legacy():
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


def test_extract_todo_and_action():
    items = extract_action_items_detailed("- TODO: fix bug\n- ACTION: deploy")
    assert len(items) == 2
    assert items[0].category == "action"
    assert items[1].category == "action"


def test_extract_fixme_hack_bug():
    text = "FIXME: broken\nHACK: workaround\nBUG: crash on login"
    items = extract_action_items_detailed(text)
    assert len(items) == 3
    assert all(i.category == "bug" for i in items)


def test_extract_note_prefix():
    items = extract_action_items_detailed("NOTE: remember this")
    assert len(items) == 1
    assert items[0].category == "note"


def test_extract_at_todo():
    items = extract_action_items_detailed("@todo refactor this module")
    assert len(items) == 1
    assert items[0].category == "action"
    assert items[0].text == "@todo refactor this module"


def test_extract_checkbox():
    items = extract_action_items_detailed("[ ] Write documentation")
    assert len(items) == 1
    assert items[0].category == "task"
    assert items[0].text == "Write documentation"


def test_extract_exclamation():
    items = extract_action_items_detailed("Ship it!")
    assert len(items) == 1
    assert items[0].category == "general"


def test_extract_priority_urgent():
    items = extract_action_items_detailed("TODO: [P0] fix production crash")
    assert len(items) == 1
    assert items[0].priority == "urgent"


def test_extract_priority_high():
    items = extract_action_items_detailed("TODO: [P1] optimize query")
    assert len(items) == 1
    assert items[0].priority == "high"


def test_extract_priority_urgent_marker():
    items = extract_action_items_detailed("ACTION: [URGENT] rollback deploy")
    assert len(items) == 1
    assert items[0].priority == "urgent"


def test_extract_deadline_bumps_priority():
    items = extract_action_items_detailed("TODO: finish report by EOD")
    assert len(items) == 1
    assert items[0].priority == "high"


def test_extract_deadline_due():
    items = extract_action_items_detailed("TODO: submit review due Friday")
    assert len(items) == 1
    assert items[0].priority == "high"


def test_extract_mixed_patterns():
    text = """
    - TODO: [P0] critical fix
    - FIXME: memory leak
    - [ ] update docs
    - @todo add logging
    - Just a normal line
    - Deploy now!
    """.strip()
    items = extract_action_items_detailed(text)
    assert len(items) == 5
    categories = [i.category for i in items]
    assert "action" in categories
    assert "bug" in categories
    assert "task" in categories
    assert "general" in categories


def test_extract_empty_text():
    items = extract_action_items_detailed("")
    assert items == []


def test_extract_no_matches():
    items = extract_action_items_detailed("Just a regular note\nWith no action items")
    assert items == []


def test_extract_endpoint(client):
    r = client.post("/notes/", json={"title": "Test", "content": "TODO: write tests\nFIXME: bug"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["text"] == "TODO: write tests"
    assert data["items"][0]["category"] == "action"


def test_extract_endpoint_not_found(client):
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404


def test_extract_endpoint_no_items(client):
    r = client.post("/notes/", json={"title": "Test", "content": "Nothing here"})
    note_id = r.json()["id"]
    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    assert r.json()["count"] == 0
    assert r.json()["items"] == []
