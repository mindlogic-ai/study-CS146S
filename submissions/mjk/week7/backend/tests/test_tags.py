def test_create_and_list_tags(client):
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 201
    tag = r.json()
    assert tag["name"] == "python"

    r = client.get("/tags/")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_create_duplicate_tag(client):
    client.post("/tags/", json={"name": "duplicate"})
    r = client.post("/tags/", json={"name": "duplicate"})
    assert r.status_code == 409


def test_delete_tag(client):
    r = client.post("/tags/", json={"name": "temp"})
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 404


def test_create_note_with_tags(client):
    t1 = client.post("/tags/", json={"name": "work"}).json()
    t2 = client.post("/tags/", json={"name": "urgent"}).json()

    r = client.post(
        "/notes/",
        json={"title": "Tagged", "content": "hello", "tag_ids": [t1["id"], t2["id"]]},
    )
    assert r.status_code == 201
    note = r.json()
    tag_names = {t["name"] for t in note["tags"]}
    assert tag_names == {"work", "urgent"}


def test_patch_note_tags(client):
    tag = client.post("/tags/", json={"name": "new-tag"}).json()
    note = client.post("/notes/", json={"title": "N", "content": "c"}).json()

    r = client.patch(f"/notes/{note['id']}", json={"tag_ids": [tag["id"]]})
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 1

    # Clear tags
    r = client.patch(f"/notes/{note['id']}", json={"tag_ids": []})
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 0


def test_create_note_with_invalid_tag(client):
    r = client.post(
        "/notes/",
        json={"title": "Bad", "content": "hello", "tag_ids": [9999]},
    )
    assert r.status_code == 404
