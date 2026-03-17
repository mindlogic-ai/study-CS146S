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


def test_delete_action_item(client):
    r = client.post("/action-items/", json={"description": "Delete me"})
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get("/action-items/")
    ids = [i["id"] for i in r.json()]
    assert item_id not in ids


def test_delete_action_item_not_found(client):
    r = client.delete("/action-items/9999")
    assert r.status_code == 404


def test_action_item_count(client):
    client.post("/action-items/", json={"description": "a"})
    client.post("/action-items/", json={"description": "b"})
    r = client.get("/action-items/count")
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_action_items_pagination(client):
    for i in range(5):
        client.post("/action-items/", json={"description": f"Item {i}"})

    r = client.get("/action-items/", params={"limit": 2, "skip": 0})
    assert len(r.json()) == 2

    r = client.get("/action-items/", params={"limit": 2, "skip": 4})
    assert len(r.json()) == 1

    r = client.get("/action-items/", params={"limit": 2, "skip": 10})
    assert len(r.json()) == 0


def test_action_items_sorting(client):
    client.post("/action-items/", json={"description": "Alpha"})
    client.post("/action-items/", json={"description": "Beta"})
    client.post("/action-items/", json={"description": "Gamma"})

    # Sort by description ascending
    r = client.get("/action-items/", params={"sort": "description"})
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs)

    # Sort by description descending
    r = client.get("/action-items/", params={"sort": "-description"})
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs, reverse=True)

    # Invalid sort field falls back to -created_at
    r = client.get("/action-items/", params={"sort": "nonexistent"})
    assert r.status_code == 200


def test_action_items_filter_with_pagination(client):
    for i in range(3):
        item = client.post("/action-items/", json={"description": f"Done {i}"}).json()
        client.put(f"/action-items/{item['id']}/complete")
    for i in range(2):
        client.post("/action-items/", json={"description": f"Open {i}"})

    # Filter completed with pagination
    r = client.get("/action-items/", params={"completed": True, "limit": 2})
    assert len(r.json()) == 2
    assert all(i["completed"] for i in r.json())

    r = client.get("/action-items/", params={"completed": True, "limit": 2, "skip": 2})
    assert len(r.json()) == 1

    # Filter open
    r = client.get("/action-items/", params={"completed": False})
    assert all(not i["completed"] for i in r.json())
    assert len(r.json()) == 2


def test_create_action_item_validation(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
