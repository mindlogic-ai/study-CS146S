"""
Test: Tag model and relationships
Plan: /markdowns/week7-task3-tag-model.md
"""


class TestTagCRUD:
    def test_should_create_tag(self, client):
        r = client.post("/tags/", json={"name": "python"})
        assert r.status_code == 201
        assert r.json()["name"] == "python"

    def test_should_list_tags(self, client):
        client.post("/tags/", json={"name": "python"})
        client.post("/tags/", json={"name": "fastapi"})
        r = client.get("/tags/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_should_return_409_for_duplicate_tag(self, client):
        client.post("/tags/", json={"name": "python"})
        r = client.post("/tags/", json={"name": "python"})
        assert r.status_code == 409

    def test_should_delete_tag(self, client):
        r = client.post("/tags/", json={"name": "python"})
        tag_id = r.json()["id"]
        r = client.delete(f"/tags/{tag_id}")
        assert r.status_code == 204

    def test_should_return_404_when_deleting_nonexistent_tag(self, client):
        r = client.delete("/tags/9999")
        assert r.status_code == 404


class TestNoteTagRelationship:
    def test_should_attach_tag_to_note(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        tag = client.post("/tags/", json={"name": "python"}).json()

        r = client.post(f"/notes/{note['id']}/tags/{tag['id']}")
        assert r.status_code == 200
        assert len(r.json()["tags"]) == 1
        assert r.json()["tags"][0]["name"] == "python"

    def test_should_attach_tag_idempotently(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        tag = client.post("/tags/", json={"name": "python"}).json()

        client.post(f"/notes/{note['id']}/tags/{tag['id']}")
        client.post(f"/notes/{note['id']}/tags/{tag['id']}")

        r = client.get(f"/notes/{note['id']}")
        assert len(r.json()["tags"]) == 1

    def test_should_detach_tag_from_note(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        tag = client.post("/tags/", json={"name": "python"}).json()

        client.post(f"/notes/{note['id']}/tags/{tag['id']}")
        r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
        assert r.status_code == 200
        assert len(r.json()["tags"]) == 0

    def test_should_return_404_for_nonexistent_note_on_attach(self, client):
        tag = client.post("/tags/", json={"name": "python"}).json()
        r = client.post(f"/notes/9999/tags/{tag['id']}")
        assert r.status_code == 404

    def test_should_return_404_for_nonexistent_tag_on_attach(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        r = client.post(f"/notes/{note['id']}/tags/9999")
        assert r.status_code == 404

    def test_should_include_tags_in_note_read(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        r = client.get(f"/notes/{note['id']}")
        assert r.json()["tags"] == []

    def test_should_cascade_delete_tag_from_notes(self, client):
        note = client.post("/notes/", json={"title": "Test", "content": "content"}).json()
        tag = client.post("/tags/", json={"name": "python"}).json()
        client.post(f"/notes/{note['id']}/tags/{tag['id']}")

        client.delete(f"/tags/{tag['id']}")
        r = client.get(f"/notes/{note['id']}")
        assert len(r.json()["tags"]) == 0
