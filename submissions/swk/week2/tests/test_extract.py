import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# -----------------------------------------------------------------------------
# Tests for extract_action_items_llm()
# -----------------------------------------------------------------------------

class TestExtractActionItemsLLM:
    """Unit tests for LLM-powered action item extraction using Gemini API."""

    def test_llm_extract_bullet_list(self):
        """Test extraction from bullet point list."""
        text = """
        - Buy groceries
        - Call the doctor
        - Submit the report
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        # Check that some expected items are extracted
        items_lower = [item.lower() for item in items]
        assert any("groceries" in item for item in items_lower)
        assert any("doctor" in item or "call" in item for item in items_lower)

    def test_llm_extract_keyword_prefixed(self):
        """Test extraction from keyword-prefixed lines."""
        text = """
        TODO: Finish the presentation
        ACTION: Review pull request
        NEXT: Schedule team meeting
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        items_lower = [item.lower() for item in items]
        assert any("presentation" in item for item in items_lower)
        assert any("review" in item or "pull request" in item for item in items_lower)

    def test_llm_extract_empty_input(self):
        """Test that empty input returns empty list."""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []
        assert extract_action_items_llm(None) == []  # type: ignore

    def test_llm_extract_no_action_items(self):
        """Test extraction from text with no clear action items."""
        text = "The weather is nice today. I enjoyed my coffee this morning."
        items = extract_action_items_llm(text)
        # Should return empty or very few items since there are no tasks
        assert len(items) <= 1

    def test_llm_extract_natural_language(self):
        """Test extraction from natural language paragraph."""
        text = """
        Tomorrow I need to finish the quarterly report and send it to my manager.
        Also, don't forget to book the flight for next week's conference.
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        items_lower = [item.lower() for item in items]
        assert any("report" in item for item in items_lower)
        assert any("flight" in item or "book" in item for item in items_lower)

    def test_llm_extract_checkbox_format(self):
        """Test extraction from checkbox format."""
        text = """
        [ ] Complete code review
        [x] Write documentation
        [ ] Deploy to staging
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 1
        items_lower = [item.lower() for item in items]
        assert any("review" in item or "deploy" in item for item in items_lower)

    def test_llm_extract_mixed_format(self):
        """Test extraction from mixed format text."""
        text = """
        Meeting notes:
        1. Discuss project timeline
        - Assign tasks to team members
        TODO: Update project documentation

        Remember to follow up with the client about the proposal.
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 3
        items_lower = [item.lower() for item in items]
        assert any("timeline" in item or "discuss" in item for item in items_lower)
        assert any("documentation" in item for item in items_lower)
