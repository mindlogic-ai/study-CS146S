def test_create_and_list_tags(client):
    r = client.post("/tags/", json={"name": "urgent"})
    assert r.status_code == 201
    tag = r.json()
    assert tag["name"] == "urgent"

    r = client.get("/tags/")
    assert r.status_code == 200
    assert any(t["name"] == "urgent" for t in r.json())


def test_create_duplicate_tag_returns_409(client):
    client.post("/tags/", json={"name": "dup"})
    r = client.post("/tags/", json={"name": "dup"})
    assert r.status_code == 409


def test_delete_tag(client):
    r = client.post("/tags/", json={"name": "temp"})
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get("/tags/")
    assert not any(t["id"] == tag_id for t in r.json())


def test_delete_tag_not_found(client):
    r = client.delete("/tags/9999")
    assert r.status_code == 404


def test_create_note_with_tags(client):
    r = client.post("/notes/", json={
        "title": "Tagged note",
        "content": "body",
        "tag_names": ["python", "fastapi"],
    })
    assert r.status_code == 201
    note = r.json()
    tag_names = {t["name"] for t in note["tags"]}
    assert tag_names == {"python", "fastapi"}


def test_patch_note_tags(client):
    r = client.post("/notes/", json={
        "title": "Note",
        "content": "body",
        "tag_names": ["old"],
    })
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={"tag_names": ["new1", "new2"]})
    assert r.status_code == 200
    tag_names = {t["name"] for t in r.json()["tags"]}
    assert tag_names == {"new1", "new2"}


def test_filter_notes_by_tag(client):
    client.post("/notes/", json={
        "title": "A", "content": "body", "tag_names": ["special"],
    })
    client.post("/notes/", json={
        "title": "B", "content": "body", "tag_names": ["other"],
    })

    r = client.get("/notes/", params={"tag": "special"})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "A"


def test_note_without_tags_returns_empty_list(client):
    r = client.post("/notes/", json={"title": "Plain", "content": "no tags"})
    assert r.status_code == 201
    assert r.json()["tags"] == []
