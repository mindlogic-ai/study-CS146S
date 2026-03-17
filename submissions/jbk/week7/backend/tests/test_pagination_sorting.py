"""Comprehensive pagination and sorting tests for notes and action items."""

import time


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _create_notes(client, titles: list[str]) -> list[dict]:
    """Create notes with the given titles and return their response dicts."""
    results = []
    for t in titles:
        r = client.post("/notes/", json={"title": t, "content": f"Content for {t}"})
        assert r.status_code == 201
        results.append(r.json())
        time.sleep(0.01)  # ensure distinct created_at timestamps
    return results


def _create_action_items(client, descriptions: list[str]) -> list[dict]:
    results = []
    for d in descriptions:
        r = client.post("/action-items/", json={"description": d})
        assert r.status_code == 201
        results.append(r.json())
        time.sleep(0.01)
    return results


# ===========================================================================
# 1. Pagination tests (notes)
# ===========================================================================


class TestNotesPagination:
    def test_limit_returns_correct_count(self, client):
        _create_notes(client, [f"Note {i}" for i in range(5)])
        resp = client.get("/notes/", params={"limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_skip_and_limit(self, client):
        notes = _create_notes(client, [f"Note {i}" for i in range(5)])
        # Default sort is -created_at so newest first
        resp = client.get("/notes/", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_skip_near_end(self, client):
        _create_notes(client, [f"Note {i}" for i in range(5)])
        resp = client.get("/notes/", params={"skip": 4, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_skip_beyond_total(self, client):
        _create_notes(client, [f"Note {i}" for i in range(5)])
        resp = client.get("/notes/", params={"skip": 10, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 0


# ===========================================================================
# 2. Pagination tests (action items)
# ===========================================================================


class TestActionItemsPagination:
    def test_limit_returns_correct_count(self, client):
        _create_action_items(client, [f"Item {i}" for i in range(5)])
        resp = client.get("/action-items/", params={"limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_skip_and_limit(self, client):
        _create_action_items(client, [f"Item {i}" for i in range(5)])
        resp = client.get("/action-items/", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_skip_near_end(self, client):
        _create_action_items(client, [f"Item {i}" for i in range(5)])
        resp = client.get("/action-items/", params={"skip": 4, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_skip_beyond_total(self, client):
        _create_action_items(client, [f"Item {i}" for i in range(5)])
        resp = client.get("/action-items/", params={"skip": 10, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 0


# ===========================================================================
# 3. Sorting tests (notes)
# ===========================================================================


class TestNotesSorting:
    def test_sort_by_title_asc(self, client):
        _create_notes(client, ["Charlie", "Alpha", "Bravo"])
        resp = client.get("/notes/", params={"sort": "title"})
        titles = [n["title"] for n in resp.json()]
        assert titles == ["Alpha", "Bravo", "Charlie"]

    def test_sort_by_title_desc(self, client):
        _create_notes(client, ["Charlie", "Alpha", "Bravo"])
        resp = client.get("/notes/", params={"sort": "-title"})
        titles = [n["title"] for n in resp.json()]
        assert titles == ["Charlie", "Bravo", "Alpha"]

    def test_sort_by_created_at_asc(self, client):
        notes = _create_notes(client, ["First", "Second", "Third"])
        resp = client.get("/notes/", params={"sort": "created_at"})
        data = resp.json()
        titles = [n["title"] for n in data]
        assert titles == ["First", "Second", "Third"]

    def test_sort_by_created_at_desc(self, client):
        _create_notes(client, ["First", "Second", "Third"])
        resp = client.get("/notes/", params={"sort": "-created_at"})
        data = resp.json()
        titles = [n["title"] for n in data]
        assert titles == ["Third", "Second", "First"]

    def test_invalid_sort_field_falls_back_to_created_at_desc(self, client):
        _create_notes(client, ["First", "Second", "Third"])
        resp = client.get("/notes/", params={"sort": "nonexistent_field"})
        assert resp.status_code == 200
        data = resp.json()
        titles = [n["title"] for n in data]
        # Fallback is -created_at (newest first)
        assert titles == ["Third", "Second", "First"]


# ===========================================================================
# 4. Sorting tests (action items)
# ===========================================================================


class TestActionItemsSorting:
    def test_sort_by_description_asc(self, client):
        _create_action_items(client, ["Zebra task", "Apple task", "Mango task"])
        resp = client.get("/action-items/", params={"sort": "description"})
        descs = [i["description"] for i in resp.json()]
        assert descs == ["Apple task", "Mango task", "Zebra task"]

    def test_sort_by_description_desc(self, client):
        _create_action_items(client, ["Zebra task", "Apple task", "Mango task"])
        resp = client.get("/action-items/", params={"sort": "-description"})
        descs = [i["description"] for i in resp.json()]
        assert descs == ["Zebra task", "Mango task", "Apple task"]

    def test_default_sort_is_created_at_desc(self, client):
        _create_action_items(client, ["First", "Second", "Third"])
        resp = client.get("/action-items/")
        descs = [i["description"] for i in resp.json()]
        assert descs == ["Third", "Second", "First"]


# ===========================================================================
# 5. Validation tests
# ===========================================================================


class TestValidation:
    def test_limit_zero_returns_422(self, client):
        resp = client.get("/notes/", params={"limit": 0})
        assert resp.status_code == 422

    def test_limit_exceeds_max_returns_422(self, client):
        resp = client.get("/notes/", params={"limit": 201})
        assert resp.status_code == 422

    def test_negative_skip_returns_422(self, client):
        resp = client.get("/notes/", params={"skip": -1})
        assert resp.status_code == 422

    def test_negative_limit_returns_422(self, client):
        resp = client.get("/notes/", params={"limit": -1})
        assert resp.status_code == 422

    def test_action_items_limit_zero_returns_422(self, client):
        resp = client.get("/action-items/", params={"limit": 0})
        assert resp.status_code == 422

    def test_action_items_limit_exceeds_max_returns_422(self, client):
        resp = client.get("/action-items/", params={"limit": 201})
        assert resp.status_code == 422

    def test_action_items_negative_skip_returns_422(self, client):
        resp = client.get("/action-items/", params={"skip": -1})
        assert resp.status_code == 422

    def test_action_items_negative_limit_returns_422(self, client):
        resp = client.get("/action-items/", params={"limit": -1})
        assert resp.status_code == 422


# ===========================================================================
# 6. Combined pagination + sorting
# ===========================================================================


class TestCombinedPaginationSorting:
    def test_notes_pagination_with_sort_asc(self, client):
        _create_notes(client, ["Delta", "Alpha", "Echo", "Bravo", "Charlie"])
        resp = client.get("/notes/", params={"sort": "title", "skip": 1, "limit": 2})
        titles = [n["title"] for n in resp.json()]
        # Sorted asc: Alpha, Bravo, Charlie, Delta, Echo  -> skip 1, limit 2 -> Bravo, Charlie
        assert titles == ["Bravo", "Charlie"]

    def test_notes_pagination_with_sort_desc(self, client):
        _create_notes(client, ["Delta", "Alpha", "Echo", "Bravo", "Charlie"])
        resp = client.get("/notes/", params={"sort": "-title", "skip": 1, "limit": 2})
        titles = [n["title"] for n in resp.json()]
        # Sorted desc: Echo, Delta, Charlie, Bravo, Alpha -> skip 1, limit 2 -> Delta, Charlie
        assert titles == ["Delta", "Charlie"]

    def test_action_items_pagination_with_sort(self, client):
        _create_action_items(client, ["Zebra", "Apple", "Mango", "Banana", "Cherry"])
        resp = client.get("/action-items/", params={"sort": "description", "skip": 2, "limit": 2})
        descs = [i["description"] for i in resp.json()]
        # Sorted asc: Apple, Banana, Cherry, Mango, Zebra -> skip 2, limit 2 -> Cherry, Mango
        assert descs == ["Cherry", "Mango"]
