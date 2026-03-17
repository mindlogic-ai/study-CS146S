import time


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


def test_pagination_skip_limit(client):
    for i in range(3):
        client.post("/action-items/", json={"description": f"Item {i}"})

    r = client.get("/action-items/", params={"skip": 0, "limit": 1, "sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    first_desc = items[0]["description"]

    r = client.get("/action-items/", params={"skip": 1, "limit": 1, "sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["description"] != first_desc


def test_pagination_skip_beyond_data(client):
    client.post("/action-items/", json={"description": "Only one"})

    r = client.get("/action-items/", params={"skip": 100})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_limit_zero(client):
    client.post("/action-items/", json={"description": "Exists"})

    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 200
    assert r.json() == []


def test_pagination_limit_exceeds_max(client):
    r = client.get("/action-items/", params={"limit": 201})
    assert r.status_code == 422


def test_sort_description_asc(client):
    client.post("/action-items/", json={"description": "Banana task"})
    client.post("/action-items/", json={"description": "Apple task"})
    client.post("/action-items/", json={"description": "Cherry task"})

    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    items = r.json()
    descs = [i["description"] for i in items]
    assert descs == sorted(descs)


def test_sort_description_desc(client):
    client.post("/action-items/", json={"description": "Banana task"})
    client.post("/action-items/", json={"description": "Apple task"})
    client.post("/action-items/", json={"description": "Cherry task"})

    r = client.get("/action-items/", params={"sort": "-description"})
    assert r.status_code == 200
    items = r.json()
    descs = [i["description"] for i in items]
    assert descs == sorted(descs, reverse=True)


def test_sort_invalid_field(client):
    client.post("/action-items/", json={"description": "First"})
    time.sleep(0.01)
    client.post("/action-items/", json={"description": "Second"})

    r = client.get("/action-items/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200
    items = r.json()
    assert items[0]["description"] == "Second"
    assert items[1]["description"] == "First"


def test_filter_with_pagination(client):
    for i in range(5):
        r = client.post("/action-items/", json={"description": f"Done {i}"})
        client.put(f"/action-items/{r.json()['id']}/complete")
    for i in range(3):
        client.post("/action-items/", json={"description": f"Pending {i}"})

    r = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    assert all(i["completed"] is True for i in items)

    r = client.get("/action-items/", params={"completed": True, "skip": 2, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    assert all(i["completed"] is True for i in items)


def test_empty_list(client):
    r = client.get("/action-items/")
    assert r.status_code == 200
    assert r.json() == []


def test_filter_no_matches(client):
    client.post("/action-items/", json={"description": "Not completed"})

    r = client.get("/action-items/", params={"completed": True})
    assert r.status_code == 200
    assert r.json() == []
