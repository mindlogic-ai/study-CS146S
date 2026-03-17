import time


def _seed_items(client, count=5):
    items = []
    for i in range(count):
        r = client.post("/action-items/", json={"description": f"Item {i}"})
        items.append(r.json())
        time.sleep(0.01)
    return items


def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


# ---- Pagination tests ----

def test_pagination_limit(client):
    _seed_items(client, 5)
    r = client.get("/action-items/", params={"limit": 3})
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_pagination_skip(client):
    _seed_items(client, 5)
    all_items = client.get("/action-items/", params={"limit": 100}).json()
    skipped = client.get("/action-items/", params={"skip": 2, "limit": 100}).json()
    assert len(skipped) == len(all_items) - 2


def test_pagination_skip_beyond_total(client):
    _seed_items(client, 3)
    r = client.get("/action-items/", params={"skip": 100})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_pages_no_overlap(client):
    _seed_items(client, 8)
    page1 = client.get("/action-items/", params={"skip": 0, "limit": 3}).json()
    page2 = client.get("/action-items/", params={"skip": 3, "limit": 3}).json()
    page1_ids = {i["id"] for i in page1}
    page2_ids = {i["id"] for i in page2}
    assert page1_ids.isdisjoint(page2_ids)


# ---- Sorting tests ----

def test_sort_by_description_asc(client):
    for desc in ["Banana", "Apple", "Cherry"]:
        client.post("/action-items/", json={"description": desc})
    r = client.get("/action-items/", params={"sort": "description"})
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs)


def test_sort_by_description_desc(client):
    for desc in ["Banana", "Apple", "Cherry"]:
        client.post("/action-items/", json={"description": desc})
    r = client.get("/action-items/", params={"sort": "-description"})
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs, reverse=True)


def test_sort_by_created_at_asc(client):
    _seed_items(client, 4)
    r = client.get("/action-items/", params={"sort": "created_at"})
    dates = [i["created_at"] for i in r.json()]
    assert dates == sorted(dates)


def test_default_sort_is_created_at_desc(client):
    _seed_items(client, 4)
    r = client.get("/action-items/")
    dates = [i["created_at"] for i in r.json()]
    assert dates == sorted(dates, reverse=True)


def test_sort_invalid_field_falls_back(client):
    _seed_items(client, 3)
    r = client.get("/action-items/", params={"sort": "bogus"})
    assert r.status_code == 200
    dates = [i["created_at"] for i in r.json()]
    assert dates == sorted(dates, reverse=True)


# ---- Filter + Pagination combined ----

def test_filter_completed_with_pagination(client):
    items = _seed_items(client, 5)
    for it in items[:3]:
        client.put(f"/action-items/{it['id']}/complete")

    r = client.get("/action-items/", params={"completed": True, "limit": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert all(i["completed"] for i in r.json())

    r = client.get("/action-items/", params={"completed": True, "limit": 100})
    assert len(r.json()) == 3


def test_filter_not_completed(client):
    items = _seed_items(client, 4)
    client.put(f"/action-items/{items[0]['id']}/complete")

    r = client.get("/action-items/", params={"completed": False})
    assert all(not i["completed"] for i in r.json())
    assert len(r.json()) == 3
