"""
Test: New endpoints (DELETE notes, GET/DELETE action items)
Plan: /markdowns/week7-task1-endpoints-validations.md
"""


class TestDeleteNote:
    def test_should_delete_note_when_exists(self, client):
        r = client.post("/notes/", json={"title": "To delete", "content": "bye"})
        note_id = r.json()["id"]

        r = client.delete(f"/notes/{note_id}")
        assert r.status_code == 204

        r = client.get(f"/notes/{note_id}")
        assert r.status_code == 404

    def test_should_return_404_when_deleting_nonexistent_note(self, client):
        r = client.delete("/notes/9999")
        assert r.status_code == 404


class TestGetActionItem:
    def test_should_return_action_item_when_exists(self, client):
        r = client.post("/action-items/", json={"description": "Test item"})
        item_id = r.json()["id"]

        r = client.get(f"/action-items/{item_id}")
        assert r.status_code == 200
        assert r.json()["description"] == "Test item"

    def test_should_return_404_when_action_item_not_found(self, client):
        r = client.get("/action-items/9999")
        assert r.status_code == 404


class TestDeleteActionItem:
    def test_should_delete_action_item_when_exists(self, client):
        r = client.post("/action-items/", json={"description": "To delete"})
        item_id = r.json()["id"]

        r = client.delete(f"/action-items/{item_id}")
        assert r.status_code == 204

        r = client.get(f"/action-items/{item_id}")
        assert r.status_code == 404

    def test_should_return_404_when_deleting_nonexistent_action_item(self, client):
        r = client.delete("/action-items/9999")
        assert r.status_code == 404
