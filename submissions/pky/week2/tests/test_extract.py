import json
import os

import pytest
from unittest.mock import MagicMock, patch

from ..app.services.extract import extract_action_items, extract_action_items_llm

# Resolve the actual module path for mocking (works whether run from project root or submissions/pky)
_EXTRACT_MODULE = extract_action_items_llm.__module__
_CLIENT_PATCH = f"{_EXTRACT_MODULE}.client"


# --- Tests for heuristic extraction (existing) ---


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


# --- Tests for LLM extraction ---


@patch(_CLIENT_PATCH)
def test_llm_extract_bullet_list(mock_client):
    """Test LLM extraction with bullet list input."""
    mock_response = MagicMock()
    mock_response.text = '["Set up database", "Write unit tests", "Deploy to staging"]'
    mock_client.models.generate_content.return_value = mock_response

    items = extract_action_items_llm("- Set up database\n- Write unit tests\n- Deploy to staging")
    assert items == ["Set up database", "Write unit tests", "Deploy to staging"]
    mock_client.models.generate_content.assert_called_once()


@patch(_CLIENT_PATCH)
def test_llm_extract_keyword_prefixed(mock_client):
    """Test LLM extraction with keyword-prefixed lines."""
    mock_response = MagicMock()
    mock_response.text = '["Review pull request", "Update documentation"]'
    mock_client.models.generate_content.return_value = mock_response

    text = "TODO: Review pull request\nAction: Update documentation\nSome random note."
    items = extract_action_items_llm(text)
    assert items == ["Review pull request", "Update documentation"]
    mock_client.models.generate_content.assert_called_once()


def test_llm_extract_empty_input():
    """Test LLM extraction with empty input returns empty list without calling API."""
    items = extract_action_items_llm("")
    assert items == []


def test_llm_extract_whitespace_only():
    """Test LLM extraction with whitespace-only input returns empty list."""
    items = extract_action_items_llm("   \n\n  ")
    assert items == []


@patch(_CLIENT_PATCH)
def test_llm_extract_malformed_json(mock_client):
    """Test graceful fallback when LLM returns malformed JSON."""
    mock_response = MagicMock()
    mock_response.text = "not valid json at all"
    mock_client.models.generate_content.return_value = mock_response

    items = extract_action_items_llm("Some notes here")
    assert items == []


@patch(_CLIENT_PATCH)
def test_llm_extract_non_array_json(mock_client):
    """Test graceful fallback when LLM returns valid JSON but not an array."""
    mock_response = MagicMock()
    mock_response.text = '{"action": "do something"}'
    mock_client.models.generate_content.return_value = mock_response

    items = extract_action_items_llm("Some notes here")
    assert items == []


@patch(_CLIENT_PATCH)
def test_llm_extract_api_error(mock_client):
    """Test graceful fallback when Gemini API raises an exception."""
    mock_client.models.generate_content.side_effect = Exception("API error")

    items = extract_action_items_llm("Some notes here")
    assert items == []
