import time


def _seed_notes(client, count=5):
    notes = []
    for i in range(count):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})
        notes.append(r.json())
        time.sleep(0.01)  # ensure distinct created_at timestamps
    return notes


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


# ---- Pagination tests ----

def test_pagination_limit(client):
    _seed_notes(client, 5)
    r = client.get("/notes/", params={"limit": 3})
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_pagination_skip(client):
    notes = _seed_notes(client, 5)
    all_notes = client.get("/notes/", params={"limit": 100}).json()
    skipped = client.get("/notes/", params={"skip": 2, "limit": 100}).json()
    assert len(skipped) == len(all_notes) - 2


def test_pagination_skip_beyond_total_returns_empty(client):
    _seed_notes(client, 3)
    r = client.get("/notes/", params={"skip": 100})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_default_limit(client):
    _seed_notes(client, 5)
    r = client.get("/notes/")
    assert r.status_code == 200
    assert len(r.json()) <= 50


def test_pagination_skip_and_limit_combined(client):
    _seed_notes(client, 10)
    page1 = client.get("/notes/", params={"skip": 0, "limit": 3}).json()
    page2 = client.get("/notes/", params={"skip": 3, "limit": 3}).json()
    page1_ids = {n["id"] for n in page1}
    page2_ids = {n["id"] for n in page2}
    assert page1_ids.isdisjoint(page2_ids)


# ---- Sorting tests ----

def test_sort_notes_by_title_asc(client):
    for title in ["Banana", "Apple", "Cherry"]:
        client.post("/notes/", json={"title": title, "content": "x"})
    r = client.get("/notes/", params={"sort": "title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles)


def test_sort_notes_by_title_desc(client):
    for title in ["Banana", "Apple", "Cherry"]:
        client.post("/notes/", json={"title": title, "content": "x"})
    r = client.get("/notes/", params={"sort": "-title"})
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles, reverse=True)


def test_sort_notes_by_created_at_asc(client):
    _seed_notes(client, 4)
    r = client.get("/notes/", params={"sort": "created_at"})
    dates = [n["created_at"] for n in r.json()]
    assert dates == sorted(dates)


def test_sort_notes_by_created_at_desc_default(client):
    _seed_notes(client, 4)
    r = client.get("/notes/")  # default is -created_at
    dates = [n["created_at"] for n in r.json()]
    assert dates == sorted(dates, reverse=True)


def test_sort_invalid_field_falls_back_to_default(client):
    _seed_notes(client, 3)
    r = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200
    dates = [n["created_at"] for n in r.json()]
    assert dates == sorted(dates, reverse=True)


def test_sort_by_id(client):
    _seed_notes(client, 4)
    r = client.get("/notes/", params={"sort": "id"})
    ids = [n["id"] for n in r.json()]
    assert ids == sorted(ids)


# ---- Search + Pagination combined ----

def test_search_with_pagination(client):
    for i in range(5):
        client.post("/notes/", json={"title": f"Match {i}", "content": "findme"})
    client.post("/notes/", json={"title": "Other", "content": "nope"})

    r = client.get("/notes/", params={"q": "findme", "limit": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2

    r = client.get("/notes/", params={"q": "findme", "limit": 100})
    assert len(r.json()) == 5
