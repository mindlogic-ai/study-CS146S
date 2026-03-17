def test_create_and_list_tags(client):
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 201
    tag = r.json()
    assert tag["name"] == "python"
    assert "id" in tag

    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 1
    assert any(t["name"] == "python" for t in tags)


def test_delete_tag(client):
    r = client.post("/tags/", json={"name": "to-delete"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 404


def test_delete_tag_not_found(client):
    r = client.delete("/tags/9999")
    assert r.status_code == 404


def test_attach_and_detach_tag(client):
    # Create a note
    r = client.post("/notes/", json={"title": "Tagged Note", "content": "Some content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create a tag
    r = client.post("/tags/", json={"name": "important"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Attach tag to note
    r = client.post(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 200

    # Verify tag appears on note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 1
    assert note["tags"][0]["name"] == "important"

    # Detach tag from note
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Verify tag removed from note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 0


def test_attach_tag_not_found(client):
    r = client.post("/notes/", json={"title": "Note", "content": "Content"})
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/tags/9999")
    assert r.status_code == 404

    r = client.post("/notes/9999/tags/1")
    assert r.status_code == 404


def test_note_read_has_empty_tags_by_default(client):
    r = client.post("/notes/", json={"title": "No Tags", "content": "Content"})
    assert r.status_code == 201
    note = r.json()
    assert note["tags"] == []


def test_tag_create_validation(client):
    r = client.post("/tags/", json={"name": ""})
    assert r.status_code == 422

    r = client.post("/tags/", json={"name": "x" * 51})
    assert r.status_code == 422
