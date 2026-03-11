import json
from unittest.mock import patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


# --- Tests for heuristic-based extraction ---


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


# --- Tests for LLM-powered extraction (TODO 2) ---


class FakeResponse:
    """Mock Gemini API response object."""

    def __init__(self, items: list[str]):
        self.text = json.dumps(items)


@patch("week2.app.services.extract.client")
def test_llm_extract_bullet_list(mock_client):
    """LLM extraction should return action items from bullet list input."""
    expected = ["Set up database", "Write API tests"]
    mock_client.models.generate_content.return_value = FakeResponse(expected)

    result = extract_action_items_llm("- Set up database\n- Write API tests")

    assert result == expected
    mock_client.models.generate_content.assert_called_once()


@patch("week2.app.services.extract.client")
def test_llm_extract_keyword_prefixed(mock_client):
    """LLM extraction should handle keyword-prefixed lines like 'todo:' or 'action:'."""
    expected = ["Fix login bug", "Deploy to staging"]
    mock_client.models.generate_content.return_value = FakeResponse(expected)

    result = extract_action_items_llm("todo: Fix login bug\naction: Deploy to staging")

    assert result == expected


@patch("week2.app.services.extract.client")
def test_llm_extract_empty_input(mock_client):
    """LLM extraction should return empty list for empty or whitespace-only input."""
    result = extract_action_items_llm("")
    assert result == []

    result = extract_action_items_llm("   ")
    assert result == []

    # Gemini client should NOT be called for empty input
    mock_client.models.generate_content.assert_not_called()


@patch("week2.app.services.extract.client")
def test_llm_extract_no_action_items(mock_client):
    """LLM extraction should return empty list when text has no actionable items."""
    mock_client.models.generate_content.return_value = FakeResponse([])

    result = extract_action_items_llm("The weather was nice today. We had lunch.")

    assert result == []


@patch("week2.app.services.extract.client")
def test_llm_extract_mixed_format(mock_client):
    """LLM extraction should handle mixed formats (bullets, checkboxes, sentences)."""
    expected = ["Set up CI pipeline", "Review PR #42", "Update docs"]
    mock_client.models.generate_content.return_value = FakeResponse(expected)

    text = """
    Meeting notes:
    - [ ] Set up CI pipeline
    action: Review PR #42
    We need to update docs before release.
    """
    result = extract_action_items_llm(text)

    assert result == expected
