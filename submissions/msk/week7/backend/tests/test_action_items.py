from backend.tests.conftest import seed_action_items


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


def test_pagination_skip_and_limit(client):
    seed_action_items(client, 10)
    r = client.get("/action-items/", params={"limit": 3})
    assert len(r.json()) == 3

    r = client.get("/action-items/", params={"skip": 8, "limit": 50})
    assert len(r.json()) == 2


def test_pagination_skip_beyond_items(client):
    seed_action_items(client, 3)
    r = client.get("/action-items/", params={"skip": 100})
    assert r.json() == []


def test_pagination_limit_zero(client):
    seed_action_items(client, 3)
    r = client.get("/action-items/", params={"limit": 0})
    assert r.json() == []


def test_pagination_limit_capped_at_200(client):
    r = client.get("/action-items/", params={"limit": 201})
    assert r.status_code == 422


def test_sort_by_description_ascending(client):
    seed_action_items(client, 5)
    r = client.get("/action-items/", params={"sort": "description"})
    descriptions = [i["description"] for i in r.json()]
    assert descriptions == sorted(descriptions)


def test_sort_by_description_descending(client):
    seed_action_items(client, 5)
    r = client.get("/action-items/", params={"sort": "-description"})
    descriptions = [i["description"] for i in r.json()]
    assert descriptions == sorted(descriptions, reverse=True)


def test_sort_by_created_at_ascending(client):
    items = seed_action_items(client, 5)
    r = client.get("/action-items/", params={"sort": "created_at"})
    ids = [i["id"] for i in r.json()]
    expected_ids = [i["id"] for i in items]
    assert ids == expected_ids


def test_sort_by_completed(client):
    items = seed_action_items(client, 3)
    client.put(f"/action-items/{items[1]['id']}/complete")

    r = client.get("/action-items/", params={"sort": "completed"})
    completed_values = [i["completed"] for i in r.json()]
    assert completed_values == sorted(completed_values)


def test_invalid_sort_field_falls_back(client):
    seed_action_items(client, 3)
    r = client.get("/action-items/", params={"sort": "nonexistent"})
    assert r.status_code == 200
    ids = [i["id"] for i in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_completed_filter_with_pagination(client):
    items = seed_action_items(client, 6)
    for i in range(4):
        client.put(f"/action-items/{items[i]['id']}/complete")

    r = client.get("/action-items/", params={"completed": True, "limit": 2})
    result = r.json()
    assert len(result) == 2
    assert all(i["completed"] for i in result)

    r = client.get("/action-items/", params={"completed": True, "skip": 2, "limit": 10})
    result = r.json()
    assert len(result) == 2

    r = client.get("/action-items/", params={"completed": False})
    result = r.json()
    assert len(result) == 2
    assert all(not i["completed"] for i in result)


def test_completed_filter_with_sorting(client):
    items = seed_action_items(client, 3)
    for item in items:
        client.put(f"/action-items/{item['id']}/complete")

    r = client.get("/action-items/", params={"completed": True, "sort": "description"})
    descriptions = [i["description"] for i in r.json()]
    assert descriptions == sorted(descriptions)
