"""
Test: Notes pagination and sorting
Plan: /markdowns/week7-task4-pagination-sorting-tests.md
"""

import time


def _create_notes(client, count):
    """Helper to create notes with distinct timestamps and alphabetical titles."""
    notes = []
    for i in range(count):
        r = client.post("/notes/", json={"title": f"Note {chr(65 + i)}", "content": f"Content {i}"})
        notes.append(r.json())
        time.sleep(0.01)
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


class TestNotesPagination:
    def test_should_limit_results(self, client):
        _create_notes(client, 5)
        r = client.get("/notes/", params={"limit": 3})
        assert len(r.json()) == 3

    def test_should_skip_results(self, client):
        notes = _create_notes(client, 5)
        all_r = client.get("/notes/", params={"sort": "created_at"}).json()
        skip_r = client.get("/notes/", params={"skip": 2, "sort": "created_at"}).json()
        assert len(skip_r) == 3
        assert skip_r[0]["id"] == all_r[2]["id"]

    def test_should_combine_skip_and_limit(self, client):
        _create_notes(client, 5)
        r = client.get("/notes/", params={"skip": 1, "limit": 2, "sort": "created_at"})
        assert len(r.json()) == 2

    def test_should_return_empty_when_skip_exceeds_total(self, client):
        _create_notes(client, 3)
        r = client.get("/notes/", params={"skip": 100})
        assert r.json() == []

    def test_should_not_overlap_pages(self, client):
        _create_notes(client, 6)
        page1 = client.get("/notes/", params={"skip": 0, "limit": 3, "sort": "created_at"}).json()
        page2 = client.get("/notes/", params={"skip": 3, "limit": 3, "sort": "created_at"}).json()
        ids1 = {n["id"] for n in page1}
        ids2 = {n["id"] for n in page2}
        assert ids1.isdisjoint(ids2)

    def test_should_return_empty_for_empty_db(self, client):
        r = client.get("/notes/")
        assert r.json() == []


class TestNotesSorting:
    def test_should_sort_by_title_asc(self, client):
        _create_notes(client, 4)
        r = client.get("/notes/", params={"sort": "title"})
        titles = [n["title"] for n in r.json()]
        assert titles == sorted(titles)

    def test_should_sort_by_title_desc(self, client):
        _create_notes(client, 4)
        r = client.get("/notes/", params={"sort": "-title"})
        titles = [n["title"] for n in r.json()]
        assert titles == sorted(titles, reverse=True)

    def test_should_sort_by_created_at_asc(self, client):
        notes = _create_notes(client, 4)
        r = client.get("/notes/", params={"sort": "created_at"})
        ids = [n["id"] for n in r.json()]
        expected_ids = [n["id"] for n in notes]
        assert ids == expected_ids

    def test_should_sort_by_created_at_desc(self, client):
        notes = _create_notes(client, 4)
        r = client.get("/notes/", params={"sort": "-created_at"})
        ids = [n["id"] for n in r.json()]
        expected_ids = [n["id"] for n in reversed(notes)]
        assert ids == expected_ids

    def test_should_fallback_for_invalid_sort_field(self, client):
        notes = _create_notes(client, 3)
        r = client.get("/notes/", params={"sort": "nonexistent"})
        assert r.status_code == 200
        ids = [n["id"] for n in r.json()]
        expected_ids = [n["id"] for n in reversed(notes)]
        assert ids == expected_ids


class TestNotesSearchWithPagination:
    def test_should_search_and_paginate(self, client):
        for i in range(5):
            client.post("/notes/", json={"title": f"Alpha {i}", "content": "searchable"})
            time.sleep(0.01)
        client.post("/notes/", json={"title": "Beta", "content": "other"})

        r = client.get("/notes/", params={"q": "searchable", "limit": 2, "sort": "created_at"})
        assert len(r.json()) == 2

        r = client.get("/notes/", params={"q": "searchable"})
        assert len(r.json()) == 5
