"""
Test: Input validation and error handling
Plan: /markdowns/week7-task1-endpoints-validations.md
"""


class TestNoteValidation:
    def test_should_reject_empty_title(self, client):
        r = client.post("/notes/", json={"title": "", "content": "some content"})
        assert r.status_code == 422

    def test_should_reject_whitespace_only_title(self, client):
        r = client.post("/notes/", json={"title": "   ", "content": "some content"})
        assert r.status_code == 422

    def test_should_reject_title_over_200_chars(self, client):
        r = client.post("/notes/", json={"title": "a" * 201, "content": "some content"})
        assert r.status_code == 422

    def test_should_reject_empty_content(self, client):
        r = client.post("/notes/", json={"title": "Valid title", "content": ""})
        assert r.status_code == 422

    def test_should_reject_patch_with_empty_title(self, client):
        r = client.post("/notes/", json={"title": "Good", "content": "content"})
        note_id = r.json()["id"]

        r = client.patch(f"/notes/{note_id}", json={"title": ""})
        assert r.status_code == 422

    def test_should_reject_patch_with_title_over_200_chars(self, client):
        r = client.post("/notes/", json={"title": "Good", "content": "content"})
        note_id = r.json()["id"]

        r = client.patch(f"/notes/{note_id}", json={"title": "a" * 201})
        assert r.status_code == 422

    def test_should_accept_valid_note(self, client):
        r = client.post("/notes/", json={"title": "Valid", "content": "Valid content"})
        assert r.status_code == 201


class TestActionItemValidation:
    def test_should_reject_empty_description(self, client):
        r = client.post("/action-items/", json={"description": ""})
        assert r.status_code == 422

    def test_should_reject_whitespace_only_description(self, client):
        r = client.post("/action-items/", json={"description": "   "})
        assert r.status_code == 422

    def test_should_reject_patch_with_empty_description(self, client):
        r = client.post("/action-items/", json={"description": "Valid"})
        item_id = r.json()["id"]

        r = client.patch(f"/action-items/{item_id}", json={"description": ""})
        assert r.status_code == 422

    def test_should_accept_valid_action_item(self, client):
        r = client.post("/action-items/", json={"description": "Do something"})
        assert r.status_code == 201


class TestQueryParamValidation:
    def test_should_reject_negative_skip_on_notes(self, client):
        r = client.get("/notes/", params={"skip": -1})
        assert r.status_code == 422

    def test_should_reject_zero_limit_on_notes(self, client):
        r = client.get("/notes/", params={"limit": 0})
        assert r.status_code == 422

    def test_should_reject_limit_over_200_on_notes(self, client):
        r = client.get("/notes/", params={"limit": 201})
        assert r.status_code == 422

    def test_should_reject_negative_skip_on_action_items(self, client):
        r = client.get("/action-items/", params={"skip": -1})
        assert r.status_code == 422

    def test_should_reject_zero_limit_on_action_items(self, client):
        r = client.get("/action-items/", params={"limit": 0})
        assert r.status_code == 422

    def test_should_return_400_for_invalid_sort_field_on_notes(self, client):
        r = client.get("/notes/", params={"sort": "nonexistent"})
        assert r.status_code == 400

    def test_should_return_400_for_invalid_sort_field_on_action_items(self, client):
        r = client.get("/action-items/", params={"sort": "nonexistent"})
        assert r.status_code == 400
