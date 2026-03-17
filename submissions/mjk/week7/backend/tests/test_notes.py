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


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "ToDelete", "content": "bye"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


def test_note_count(client):
    client.post("/notes/", json={"title": "A", "content": "a"})
    client.post("/notes/", json={"title": "B", "content": "b"})
    r = client.get("/notes/count")
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_notes_pagination(client):
    # Create 5 notes
    for i in range(5):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    # Get first page (limit 2)
    r = client.get("/notes/", params={"limit": 2, "skip": 0})
    assert r.status_code == 200
    assert len(r.json()) == 2

    # Get second page
    r = client.get("/notes/", params={"limit": 2, "skip": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2

    # Get last page
    r = client.get("/notes/", params={"limit": 2, "skip": 4})
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Skip beyond total
    r = client.get("/notes/", params={"limit": 2, "skip": 10})
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_notes_sorting(client):
    client.post("/notes/", json={"title": "Alpha", "content": "first"})
    client.post("/notes/", json={"title": "Beta", "content": "second"})
    client.post("/notes/", json={"title": "Gamma", "content": "third"})

    # Sort by title ascending
    r = client.get("/notes/", params={"sort": "title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles)

    # Sort by title descending
    r = client.get("/notes/", params={"sort": "-title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles, reverse=True)

    # Sort by created_at ascending
    r = client.get("/notes/", params={"sort": "created_at"})
    dates = [n["created_at"] for n in r.json()]
    assert dates == sorted(dates)

    # Invalid sort field falls back to -created_at
    r = client.get("/notes/", params={"sort": "nonexistent"})
    assert r.status_code == 200
    dates = [n["created_at"] for n in r.json()]
    assert dates == sorted(dates, reverse=True)


def test_notes_search_with_pagination(client):
    for i in range(4):
        client.post("/notes/", json={"title": f"Match {i}", "content": "findme"})
    client.post("/notes/", json={"title": "Other", "content": "nope"})

    r = client.get("/notes/", params={"q": "findme", "limit": 2})
    assert len(r.json()) == 2

    r = client.get("/notes/", params={"q": "findme", "limit": 2, "skip": 2})
    assert len(r.json()) == 2

    r = client.get("/notes/", params={"q": "findme", "limit": 2, "skip": 4})
    assert len(r.json()) == 0


def test_create_note_validation(client):
    r = client.post("/notes/", json={"title": "", "content": "x"})
    assert r.status_code == 422

    r = client.post("/notes/", json={"title": "x", "content": ""})
    assert r.status_code == 422

    r = client.post("/notes/", json={"title": "a" * 201, "content": "x"})
    assert r.status_code == 422
