def test_create_and_list_tags(client):
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 201
    tag = r.json()
    assert tag["name"] == "python"
    assert "id" in tag
    assert "created_at" in tag

    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 1
    assert tags[0]["name"] == "python"


def test_create_duplicate_tag(client):
    client.post("/tags/", json={"name": "duplicate"})
    r = client.post("/tags/", json={"name": "duplicate"})
    assert r.status_code == 409


def test_delete_tag(client):
    r = client.post("/tags/", json={"name": "to-delete"})
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get("/tags/")
    assert all(t["name"] != "to-delete" for t in r.json())


def test_delete_tag_not_found(client):
    r = client.delete("/tags/9999")
    assert r.status_code == 404


def test_attach_tag_to_note(client):
    note_r = client.post("/notes/", json={"title": "Tagged", "content": "content"})
    note_id = note_r.json()["id"]
    tag_r = client.post("/tags/", json={"name": "important"})
    tag_id = tag_r.json()["id"]

    r = client.post(f"/tags/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 201

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 1
    assert note["tags"][0]["name"] == "important"


def test_attach_tag_duplicate(client):
    note_r = client.post("/notes/", json={"title": "Note", "content": "c"})
    note_id = note_r.json()["id"]
    tag_r = client.post("/tags/", json={"name": "dup-attach"})
    tag_id = tag_r.json()["id"]

    client.post(f"/tags/notes/{note_id}/tags/{tag_id}")
    r = client.post(f"/tags/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 409


def test_remove_tag_from_note(client):
    note_r = client.post("/notes/", json={"title": "Note", "content": "c"})
    note_id = note_r.json()["id"]
    tag_r = client.post("/tags/", json={"name": "removable"})
    tag_id = tag_r.json()["id"]

    client.post(f"/tags/notes/{note_id}/tags/{tag_id}")
    r = client.delete(f"/tags/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert len(r.json()["tags"]) == 0


def test_remove_tag_not_attached(client):
    note_r = client.post("/notes/", json={"title": "Note", "content": "c"})
    note_id = note_r.json()["id"]
    tag_r = client.post("/tags/", json={"name": "not-attached"})
    tag_id = tag_r.json()["id"]

    r = client.delete(f"/tags/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 404


def test_note_read_includes_empty_tags(client):
    r = client.post("/notes/", json={"title": "No tags", "content": "c"})
    note = r.json()
    assert note["tags"] == []
