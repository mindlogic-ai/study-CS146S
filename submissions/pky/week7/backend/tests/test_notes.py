def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_extract_from_note_endpoint(client):
    content = "TODO: urgent fix by Friday @alice\nRegular line\nShip it!"
    r = client.post("/notes/", json={"title": "Extract Test", "content": content})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2

    assert items[0]["text"] == "TODO: urgent fix by Friday @alice"
    assert items[0]["priority"] == "high"
    assert items[0]["assignees"] == ["alice"]

    assert items[1]["text"] == "Ship it!"
    assert items[1]["priority"] == "medium"


def test_extract_from_note_not_found(client):
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404
