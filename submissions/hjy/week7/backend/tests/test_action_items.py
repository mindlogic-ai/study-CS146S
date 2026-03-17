"""
Test: Action items pagination and sorting
Plan: /markdowns/week7-task4-pagination-sorting-tests.md
"""

import time


def _create_items(client, count, completed=False):
    """Helper to create action items with distinct timestamps."""
    items = []
    for i in range(count):
        r = client.post("/action-items/", json={"description": f"Item {chr(65 + i)}"})
        item = r.json()
        if completed:
            client.put(f"/action-items/{item['id']}/complete")
            item["completed"] = True
        items.append(item)
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


class TestActionItemsPagination:
    def test_should_limit_results(self, client):
        _create_items(client, 5)
        r = client.get("/action-items/", params={"limit": 3})
        assert len(r.json()) == 3

    def test_should_skip_results(self, client):
        _create_items(client, 5)
        all_r = client.get("/action-items/", params={"sort": "created_at"}).json()
        skip_r = client.get("/action-items/", params={"skip": 2, "sort": "created_at"}).json()
        assert len(skip_r) == 3
        assert skip_r[0]["id"] == all_r[2]["id"]

    def test_should_combine_skip_and_limit(self, client):
        _create_items(client, 5)
        r = client.get("/action-items/", params={"skip": 1, "limit": 2, "sort": "created_at"})
        assert len(r.json()) == 2

    def test_should_return_empty_when_skip_exceeds_total(self, client):
        _create_items(client, 3)
        r = client.get("/action-items/", params={"skip": 100})
        assert r.json() == []

    def test_should_not_overlap_pages(self, client):
        _create_items(client, 6)
        page1 = client.get("/action-items/", params={"skip": 0, "limit": 3, "sort": "created_at"}).json()
        page2 = client.get("/action-items/", params={"skip": 3, "limit": 3, "sort": "created_at"}).json()
        ids1 = {i["id"] for i in page1}
        ids2 = {i["id"] for i in page2}
        assert ids1.isdisjoint(ids2)

    def test_should_return_empty_for_empty_db(self, client):
        r = client.get("/action-items/")
        assert r.json() == []


class TestActionItemsSorting:
    def test_should_sort_by_description_asc(self, client):
        _create_items(client, 4)
        r = client.get("/action-items/", params={"sort": "description"})
        descs = [i["description"] for i in r.json()]
        assert descs == sorted(descs)

    def test_should_sort_by_description_desc(self, client):
        _create_items(client, 4)
        r = client.get("/action-items/", params={"sort": "-description"})
        descs = [i["description"] for i in r.json()]
        assert descs == sorted(descs, reverse=True)

    def test_should_sort_by_created_at_asc(self, client):
        items = _create_items(client, 4)
        r = client.get("/action-items/", params={"sort": "created_at"})
        ids = [i["id"] for i in r.json()]
        expected_ids = [i["id"] for i in items]
        assert ids == expected_ids

    def test_should_sort_by_created_at_desc(self, client):
        items = _create_items(client, 4)
        r = client.get("/action-items/", params={"sort": "-created_at"})
        ids = [i["id"] for i in r.json()]
        expected_ids = [i["id"] for i in reversed(items)]
        assert ids == expected_ids

    def test_should_fallback_for_invalid_sort_field(self, client):
        items = _create_items(client, 3)
        r = client.get("/action-items/", params={"sort": "nonexistent"})
        assert r.status_code == 200
        ids = [i["id"] for i in r.json()]
        expected_ids = [i["id"] for i in reversed(items)]
        assert ids == expected_ids


class TestActionItemsFilterWithPagination:
    def test_should_filter_completed_with_pagination(self, client):
        _create_items(client, 3, completed=True)
        _create_items(client, 2, completed=False)
        r = client.get("/action-items/", params={"completed": True, "limit": 2})
        items = r.json()
        assert len(items) == 2
        assert all(i["completed"] for i in items)

    def test_should_filter_not_completed(self, client):
        _create_items(client, 2, completed=True)
        _create_items(client, 3, completed=False)
        r = client.get("/action-items/", params={"completed": False})
        items = r.json()
        assert len(items) == 3
        assert all(not i["completed"] for i in items)

    def test_should_return_empty_when_no_filter_matches(self, client):
        _create_items(client, 3, completed=False)
        r = client.get("/action-items/", params={"completed": True})
        assert r.json() == []
