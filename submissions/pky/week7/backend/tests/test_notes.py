import time


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


def test_pagination_skip_limit(client):
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    r = client.get("/notes/", params={"skip": 0, "limit": 1, "sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    first_title = items[0]["title"]

    r = client.get("/notes/", params={"skip": 1, "limit": 1, "sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] != first_title


def test_pagination_skip_beyond_data(client):
    client.post("/notes/", json={"title": "Only", "content": "One"})

    r = client.get("/notes/", params={"skip": 100})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_limit_zero(client):
    client.post("/notes/", json={"title": "Exists", "content": "Here"})

    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_limit_exceeds_max(client):
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422


def test_sort_title_asc(client):
    client.post("/notes/", json={"title": "Banana", "content": "b"})
    client.post("/notes/", json={"title": "Apple", "content": "a"})
    client.post("/notes/", json={"title": "Cherry", "content": "c"})

    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    items = r.json()
    titles = [n["title"] for n in items]
    assert titles == sorted(titles)


def test_sort_title_desc(client):
    client.post("/notes/", json={"title": "Banana", "content": "b"})
    client.post("/notes/", json={"title": "Apple", "content": "a"})
    client.post("/notes/", json={"title": "Cherry", "content": "c"})

    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    items = r.json()
    titles = [n["title"] for n in items]
    assert titles == sorted(titles, reverse=True)


def test_sort_created_at(client):
    client.post("/notes/", json={"title": "First", "content": "1"})
    time.sleep(0.01)
    client.post("/notes/", json={"title": "Second", "content": "2"})
    time.sleep(0.01)
    client.post("/notes/", json={"title": "Third", "content": "3"})

    r = client.get("/notes/", params={"sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert items[0]["title"] == "First"
    assert items[-1]["title"] == "Third"

    r = client.get("/notes/", params={"sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert items[0]["title"] == "Third"
    assert items[-1]["title"] == "First"


def test_sort_invalid_field(client):
    client.post("/notes/", json={"title": "First", "content": "1"})
    time.sleep(0.01)
    client.post("/notes/", json={"title": "Second", "content": "2"})

    r = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200
    items = r.json()
    assert items[0]["title"] == "Second"
    assert items[1]["title"] == "First"


def test_search_with_pagination(client):
    for i in range(5):
        client.post("/notes/", json={"title": f"Match {i}", "content": "searchable"})
    client.post("/notes/", json={"title": "Other", "content": "different"})

    r = client.get("/notes/", params={"q": "searchable", "skip": 0, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2

    r = client.get("/notes/", params={"q": "searchable", "skip": 2, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2


def test_empty_database(client):
    r = client.get("/notes/")
    assert r.status_code == 200
    assert r.json() == []


def test_single_item(client):
    client.post("/notes/", json={"title": "Solo", "content": "Only one"})

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Solo"
