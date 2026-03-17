from backend.tests.conftest import seed_notes


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


def test_pagination_skip_and_limit(client):
    seed_notes(client, 10)
    r = client.get("/notes/", params={"limit": 3})
    assert len(r.json()) == 3

    r = client.get("/notes/", params={"skip": 8, "limit": 50})
    assert len(r.json()) == 2


def test_pagination_skip_beyond_items(client):
    seed_notes(client, 3)
    r = client.get("/notes/", params={"skip": 100})
    assert r.json() == []


def test_pagination_limit_zero(client):
    seed_notes(client, 3)
    r = client.get("/notes/", params={"limit": 0})
    assert r.json() == []


def test_pagination_limit_capped_at_200(client):
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422


def test_sort_by_title_ascending(client):
    seed_notes(client, 5)
    r = client.get("/notes/", params={"sort": "title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles)


def test_sort_by_title_descending(client):
    seed_notes(client, 5)
    r = client.get("/notes/", params={"sort": "-title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles, reverse=True)


def test_sort_by_created_at_ascending(client):
    notes = seed_notes(client, 5)
    r = client.get("/notes/", params={"sort": "created_at"})
    ids = [n["id"] for n in r.json()]
    expected_ids = [n["id"] for n in notes]
    assert ids == expected_ids


def test_sort_by_created_at_descending(client):
    notes = seed_notes(client, 5)
    r = client.get("/notes/", params={"sort": "-created_at"})
    ids = [n["id"] for n in r.json()]
    expected_ids = [n["id"] for n in reversed(notes)]
    assert ids == expected_ids


def test_invalid_sort_field_falls_back(client):
    seed_notes(client, 3)
    r = client.get("/notes/", params={"sort": "nonexistent"})
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_search_with_pagination(client):
    for i in range(5):
        client.post("/notes/", json={"title": f"Alpha {i}", "content": "match"})
    for i in range(3):
        client.post("/notes/", json={"title": f"Beta {i}", "content": "other"})

    r = client.get("/notes/", params={"q": "Alpha", "limit": 2})
    items = r.json()
    assert len(items) == 2
    assert all("Alpha" in n["title"] for n in items)

    r = client.get("/notes/", params={"q": "Alpha", "skip": 3, "limit": 10})
    items = r.json()
    assert len(items) == 2


def test_search_with_sorting(client):
    client.post("/notes/", json={"title": "Zebra", "content": "match"})
    client.post("/notes/", json={"title": "Apple", "content": "match"})

    r = client.get("/notes/", params={"q": "match", "sort": "title"})
    titles = [n["title"] for n in r.json()]
    assert titles == ["Apple", "Zebra"]


def test_combined_search_pagination_sorting(client):
    for i in range(10):
        client.post("/notes/", json={"title": f"Task {i:03d}", "content": "work"})
    client.post("/notes/", json={"title": "Unrelated", "content": "play"})

    r = client.get("/notes/", params={"q": "work", "sort": "title", "skip": 2, "limit": 3})
    items = r.json()
    assert len(items) == 3
    titles = [n["title"] for n in items]
    assert titles == ["Task 002", "Task 003", "Task 004"]
