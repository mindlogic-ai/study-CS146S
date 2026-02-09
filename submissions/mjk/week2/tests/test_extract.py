import json
from unittest.mock import MagicMock, patch

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


# --- LLM-based extraction tests (Gemini API mocked) ---


def _mock_gemini_response(items: list[str]) -> MagicMock:
    """Create a mock Gemini response with the given items as JSON."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(items)
    return mock_resp


@patch("submissions.mjk.week2.app.services.extract.client")
def test_llm_extract_bullet_list(mock_client):
    mock_client.models.generate_content.return_value = _mock_gemini_response(
        ["Set up database", "Implement API endpoint", "Write tests"]
    )

    text = """
    Notes from meeting:
    - Set up database
    - Implement API endpoint
    - Write tests
    Some narrative sentence.
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    assert "Set up database" in items
    assert "Implement API endpoint" in items
    assert "Write tests" in items


@patch("submissions.mjk.week2.app.services.extract.client")
def test_llm_extract_keyword_prefixed(mock_client):
    mock_client.models.generate_content.return_value = _mock_gemini_response(
        ["Fix login bug", "Update README", "Deploy to staging"]
    )

    text = """
    todo: Fix login bug
    action: Update README
    next: Deploy to staging
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    assert "Fix login bug" in items
    assert "Update README" in items
    assert "Deploy to staging" in items


@patch("submissions.mjk.week2.app.services.extract.client")
def test_llm_extract_empty_input(mock_client):
    mock_client.models.generate_content.return_value = _mock_gemini_response([])

    items = extract_action_items_llm("")
    assert items == []


@patch("submissions.mjk.week2.app.services.extract.client")
def test_llm_extract_no_action_items(mock_client):
    mock_client.models.generate_content.return_value = _mock_gemini_response([])

    text = "The weather was nice today. We had a good lunch."
    items = extract_action_items_llm(text)
    assert items == []


@patch("submissions.mjk.week2.app.services.extract.client")
def test_llm_extract_mixed_content(mock_client):
    mock_client.models.generate_content.return_value = _mock_gemini_response(
        ["Review PR #42", "Schedule follow-up meeting"]
    )

    text = """
    Meeting went well overall. The team discussed performance issues.
    - Review PR #42
    We also talked about the upcoming deadline.
    - Schedule follow-up meeting
    Everyone seemed happy with the progress.
    """
    items = extract_action_items_llm(text)
    assert len(items) == 2
    assert "Review PR #42" in items
    assert "Schedule follow-up meeting" in items
