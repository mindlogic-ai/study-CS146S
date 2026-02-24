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


def test_get_note_by_id(client):
    r = client.post("/notes/", json={"title": "Fetch me", "content": "body"})
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Fetch me"


def test_get_note_not_found(client):
    r = client.get("/notes/9999")
    assert r.status_code == 404


def test_update_note(client):
    r = client.post("/notes/", json={"title": "Old", "content": "old body"})
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={"title": "New"})
    assert r.status_code == 200
    assert r.json()["title"] == "New"
    assert r.json()["content"] == "old body"


def test_update_note_not_found(client):
    r = client.patch("/notes/9999", json={"title": "X"})
    assert r.status_code == 404


def test_update_note_empty_body(client):
    r = client.post("/notes/", json={"title": "T", "content": "C"})
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={})
    assert r.status_code == 400


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Del", "content": "me"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


def test_extract_from_note(client):
    r = client.post(
        "/notes/",
        json={"title": "Tasks", "content": "TODO: write tests\nShip it!\n#urgent #backend"},
    )
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()
    assert "TODO: write tests" in data["action_items"]
    assert "Ship it!" in data["action_items"]
    assert "urgent" in data["tags"]
    assert "backend" in data["tags"]


def test_extract_from_note_not_found(client):
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404


def test_create_note_validation_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "body"})
    assert r.status_code == 422


def test_create_note_validation_empty_content(client):
    r = client.post("/notes/", json={"title": "T", "content": ""})
    assert r.status_code == 422


def test_search_no_results(client):
    r = client.get("/notes/search/", params={"q": "nonexistent_xyz"})
    assert r.status_code == 200
    assert r.json() == []
