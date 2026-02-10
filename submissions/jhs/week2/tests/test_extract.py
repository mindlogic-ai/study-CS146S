import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ..app.services import extract as extract_module
from ..app.services.extract import extract_action_items, extract_action_items_llm


# --- Existing heuristic tests ---


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


# --- TODO 2: Unit tests for extract_action_items_llm() ---


def _mock_gemini_response(items: list[str]) -> MagicMock:
    """Helper to build a fake Gemini response with a .parsed attribute."""
    parsed = MagicMock()
    parsed.items = items
    response = MagicMock()
    response.parsed = parsed
    return response


class TestExtractActionItemsLlm:
    """Tests for the LLM-powered extraction function."""

    def test_empty_input_returns_empty(self):
        """Empty or whitespace-only input should return [] without calling the API."""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []

    def test_bullet_list(self):
        """Bullet-list notes should be parsed into individual action items."""
        expected = ["Set up database", "Write API tests", "Deploy server"]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _mock_gemini_response(expected)

        with patch.object(extract_module, "client", mock_client):
            result = extract_action_items_llm(
                "- Set up database\n- Write API tests\n- Deploy server"
            )
        assert result == expected

    def test_keyword_prefixed_lines(self):
        """Lines starting with todo:/action:/next: should be extracted."""
        expected = ["Review the PR", "Schedule meeting"]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _mock_gemini_response(expected)

        with patch.object(extract_module, "client", mock_client):
            result = extract_action_items_llm(
                "todo: Review the PR\naction: Schedule meeting\nSome context."
            )
        assert result == expected

    def test_no_action_items(self):
        """Text with no action items should return an empty list."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _mock_gemini_response([])

        with patch.object(extract_module, "client", mock_client):
            result = extract_action_items_llm("The weather is nice today.")
        assert result == []

    def test_mixed_format_notes(self):
        """Notes mixing bullets, checkboxes, and prose should all be extracted."""
        expected = [
            "Set up database",
            "Implement endpoint",
            "Write tests",
            "Review PR",
        ]
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _mock_gemini_response(expected)

        text = """
        Meeting notes:
        - [ ] Set up database
        * Implement endpoint
        1. Write tests
        todo: Review PR
        Some narrative context that isn't an action item.
        """
        with patch.object(extract_module, "client", mock_client):
            result = extract_action_items_llm(text)
        assert result == expected
