def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_note(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note = r.json()
    note_id = note["id"]

    # Partial update (title only)
    update_payload = {"title": "Updated Title"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["title"] == "Updated Title"
    assert updated["content"] == "Original Content"
    assert updated["id"] == note_id


def test_update_note_full(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note = r.json()
    note_id = note["id"]

    # Full update (both title and content)
    update_payload = {"title": "New Title", "content": "New Content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["title"] == "New Title"
    assert updated["content"] == "New Content"
    assert updated["id"] == note_id


def test_update_note_not_found(client):
    # Try to update a non-existent note
    update_payload = {"title": "Updated Title"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404, r.text


def test_delete_note(client):
    # Create a note first
    payload = {"title": "To Delete", "content": "Will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note = r.json()
    note_id = note["id"]

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 200, r.text

    # Verify it's gone
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404, r.text


def test_delete_note_not_found(client):
    # Try to delete a non-existent note
    r = client.delete("/notes/99999")
    assert r.status_code == 404, r.text
