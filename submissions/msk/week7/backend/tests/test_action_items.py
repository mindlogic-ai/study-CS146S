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


def test_get_action_item_by_id(client):
    r = client.post("/action-items/", json={"description": "Find me"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    assert r.json()["description"] == "Find me"


def test_get_action_item_not_found(client):
    r = client.get("/action-items/9999")
    assert r.status_code == 404


def test_delete_action_item(client):
    r = client.post("/action-items/", json={"description": "To delete"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_delete_action_item_not_found(client):
    r = client.delete("/action-items/9999")
    assert r.status_code == 404


def test_search_action_items(client):
    client.post("/action-items/", json={"description": "Write unit tests"})
    client.post("/action-items/", json={"description": "Deploy to prod"})

    r = client.get("/action-items/", params={"q": "unit"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert "unit" in items[0]["description"].lower()


def test_create_action_item_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
