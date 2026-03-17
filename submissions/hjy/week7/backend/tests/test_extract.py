"""
Test: Extended extraction logic
Plan: /markdowns/week7-task2-extraction-logic.md
"""

from backend.app.services.extract import ExtractedItem, extract_action_items


class TestKeywordMatching:
    def test_should_match_todo(self):
        items = extract_action_items("TODO: write tests")
        assert len(items) == 1
        assert items[0].text == "TODO: write tests"

    def test_should_match_action(self):
        items = extract_action_items("ACTION: review PR")
        assert len(items) == 1

    def test_should_match_fixme(self):
        items = extract_action_items("FIXME: broken query")
        assert len(items) == 1

    def test_should_match_bug(self):
        items = extract_action_items("BUG: null pointer crash")
        assert len(items) == 1

    def test_should_match_hack(self):
        items = extract_action_items("HACK: temporary workaround")
        assert len(items) == 1

    def test_should_match_task(self):
        items = extract_action_items("TASK: deploy to staging")
        assert len(items) == 1

    def test_should_match_followup(self):
        items = extract_action_items("FOLLOW-UP: check results")
        assert len(items) == 1

    def test_should_match_reminder(self):
        items = extract_action_items("REMINDER: send report")
        assert len(items) == 1

    def test_should_match_exclamation(self):
        items = extract_action_items("Ship it!")
        assert len(items) == 1

    def test_should_not_match_plain_text(self):
        items = extract_action_items("This is just a note")
        assert len(items) == 0


class TestPriority:
    def test_should_detect_high_urgent(self):
        items = extract_action_items("TODO: urgent fix needed")
        assert items[0].priority == "high"

    def test_should_detect_high_critical(self):
        items = extract_action_items("BUG: critical security issue")
        assert items[0].priority == "high"

    def test_should_detect_high_asap(self):
        items = extract_action_items("TODO: deploy asap")
        assert items[0].priority == "high"

    def test_should_detect_high_p0(self):
        items = extract_action_items("TODO: [P0] fix login")
        assert items[0].priority == "high"

    def test_should_detect_low_nice_to_have(self):
        items = extract_action_items("TODO: nice to have feature")
        assert items[0].priority == "low"

    def test_should_detect_low_eventually(self):
        items = extract_action_items("TODO: eventually refactor this")
        assert items[0].priority == "low"

    def test_should_detect_low_p2(self):
        items = extract_action_items("TODO: [P2] cleanup")
        assert items[0].priority == "low"

    def test_should_default_to_medium(self):
        items = extract_action_items("TODO: write tests")
        assert items[0].priority == "medium"


class TestDeadline:
    def test_should_extract_by_pattern(self):
        items = extract_action_items("TODO: finish by Friday")
        assert items[0].deadline == "Friday"

    def test_should_extract_due_pattern(self):
        items = extract_action_items("TODO: report due 2026-03-20")
        assert items[0].deadline == "2026-03-20"

    def test_should_extract_before_pattern(self):
        items = extract_action_items("TODO: submit before March 20")
        assert items[0].deadline == "March 20"

    def test_should_return_none_when_no_deadline(self):
        items = extract_action_items("TODO: write docs")
        assert items[0].deadline is None


class TestCategory:
    def test_should_detect_bug(self):
        items = extract_action_items("BUG: null pointer crash")
        assert items[0].category == "bug"

    def test_should_detect_bug_from_fixme(self):
        items = extract_action_items("FIXME: broken query")
        assert items[0].category == "bug"

    def test_should_detect_review(self):
        items = extract_action_items("TODO: review PR #42")
        assert items[0].category == "review"

    def test_should_detect_feature(self):
        items = extract_action_items("TODO: implement search feature")
        assert items[0].category == "feature"

    def test_should_default_to_task(self):
        items = extract_action_items("TODO: write tests")
        assert items[0].category == "task"


class TestReturnType:
    def test_should_return_extracted_item_dataclass(self):
        items = extract_action_items("TODO: test")
        assert isinstance(items[0], ExtractedItem)

    def test_should_handle_empty_text(self):
        items = extract_action_items("")
        assert items == []

    def test_should_handle_multiline(self):
        text = """
        TODO: first task
        Just a note
        BUG: critical crash
        Another note
        Ship it!
        """
        items = extract_action_items(text)
        assert len(items) == 3

    def test_combined_extraction(self):
        text = "TODO: [P0] fix login bug by Friday"
        items = extract_action_items(text)
        assert items[0].priority == "high"
        assert items[0].deadline == "Friday"
        assert items[0].category == "bug"


class TestExtractEndpoint:
    def test_should_extract_from_note(self, client):
        r = client.post("/notes/", json={"title": "Meeting", "content": "TODO: write report\nBUG: fix crash"})
        note_id = r.json()["id"]

        r = client.post(f"/notes/{note_id}/extract")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        assert data[0]["text"] == "TODO: write report"

    def test_should_return_404_for_nonexistent_note(self, client):
        r = client.post("/notes/9999/extract")
        assert r.status_code == 404
