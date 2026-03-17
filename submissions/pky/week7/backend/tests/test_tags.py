def test_create_and_list_tags(client):
    r = client.post("/tags/", json={"name": "urgent"})
    assert r.status_code == 201
    tag = r.json()
    assert tag["name"] == "urgent"
    assert "id" in tag

    r = client.post("/tags/", json={"name": "work"})
    assert r.status_code == 201

    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 2


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
    assert len(r.json()) == 0


def test_delete_tag_not_found(client):
    r = client.delete("/tags/999")
    assert r.status_code == 404


def test_attach_tag_to_note(client):
    note = client.post("/notes/", json={"title": "N1", "content": "C1"}).json()
    tag = client.post("/tags/", json={"name": "t1"}).json()

    r = client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "t1"


def test_attach_tag_idempotent(client):
    note = client.post("/notes/", json={"title": "N2", "content": "C2"}).json()
    tag = client.post("/tags/", json={"name": "t2"}).json()

    client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    r = client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 1


def test_detach_tag_from_note(client):
    note = client.post("/notes/", json={"title": "N3", "content": "C3"}).json()
    tag = client.post("/tags/", json={"name": "t3"}).json()

    client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 0


def test_note_read_includes_tags(client):
    note = client.post("/notes/", json={"title": "N4", "content": "C4"}).json()
    tag = client.post("/tags/", json={"name": "t4"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert len(data["tags"]) == 1


def test_cascade_delete_tag_cleans_note_tags(client):
    note = client.post("/notes/", json={"title": "N5", "content": "C5"}).json()
    tag = client.post("/tags/", json={"name": "t5"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")

    client.delete(f"/tags/{tag['id']}")

    r = client.get(f"/notes/{note['id']}")
    assert len(r.json()["tags"]) == 0
