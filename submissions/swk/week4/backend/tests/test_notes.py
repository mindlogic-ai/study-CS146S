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


# --- Task 5: PUT /notes/{id} (edit) ---
def test_update_note(client):
    # Create a note first
    r = client.post("/notes/", json={"title": "Original", "content": "Original content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Update title only (partial update)
    r = client.put(f"/notes/{note_id}", json={"title": "Updated Title"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"  # content unchanged

    # Update content only
    r = client.put(f"/notes/{note_id}", json={"content": "Updated content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"  # title unchanged
    assert data["content"] == "Updated content"

    # Update both
    r = client.put(f"/notes/{note_id}", json={"title": "Final", "content": "Final content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Final"
    assert data["content"] == "Final content"


def test_update_note_not_found(client):
    r = client.put("/notes/9999", json={"title": "Nope"})
    assert r.status_code == 404


# --- Task 5: DELETE /notes/{id} ---
def test_delete_note(client):
    # Create a note
    r = client.post("/notes/", json={"title": "To Delete", "content": "Bye"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Delete it
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 200

    # Verify it's gone
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


# --- Task 6: Validation ---
def test_create_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "", "content": "Some content"})
    assert r.status_code == 422


def test_create_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "Valid Title", "content": ""})
    assert r.status_code == 422


# --- Task 2: Case-insensitive search ---
def test_search_case_insensitive(client):
    client.post("/notes/", json={"title": "Python Tips", "content": "Use list comprehensions"})

    # Search with different case should still find it
    r = client.get("/notes/search/", params={"q": "python"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/", params={"q": "PYTHON"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
