import os

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm

# --- Heuristic extraction tests (existing) ---


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


# --- LLM extraction tests (TODO 2) ---


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set",
)
class TestExtractActionItemsLLM:
    """Integration tests for LLM-powered action item extraction."""

    def test_llm_extract_bullet_list(self):
        """LLM should extract action items from bullet lists."""
        text = """
        Meeting notes:
        - Set up the database schema
        - Implement the REST API
        - Write integration tests
        """.strip()
        items = extract_action_items_llm(text)
        assert len(items) >= 3
        # Check that core concepts are present (LLM may rephrase slightly)
        combined = " ".join(items).lower()
        assert "database" in combined
        assert "api" in combined
        assert "test" in combined

    def test_llm_extract_keyword_prefixed(self):
        """LLM should extract action items from keyword-prefixed lines."""
        text = """
        TODO: Refactor the authentication module
        Action: Update the deployment script
        Next: Review pull requests
        """.strip()
        items = extract_action_items_llm(text)
        assert len(items) >= 3
        combined = " ".join(items).lower()
        assert "refactor" in combined or "authentication" in combined
        assert "deployment" in combined or "update" in combined
        assert "review" in combined or "pull request" in combined

    def test_llm_extract_empty_input(self):
        """LLM should return empty list for empty input."""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []

    def test_llm_extract_narrative_text(self):
        """LLM should extract action items from narrative/imperative sentences."""
        text = (
            "We need to fix the login bug before Friday. "
            "Also, update the documentation and deploy to staging."
        )
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        combined = " ".join(items).lower()
        assert "login" in combined or "bug" in combined or "fix" in combined
        assert "documentation" in combined or "deploy" in combined
