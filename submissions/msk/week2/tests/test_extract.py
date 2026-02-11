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


def test_llm_extract_bullet_list():
    text = """
    - Set up database
    - Implement API endpoint
    - Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) >= 3
    assert any("database" in item.lower() for item in items)
    assert any("api" in item.lower() or "endpoint" in item.lower() for item in items)
    assert any("test" in item.lower() for item in items)


def test_llm_extract_keyword_prefixed():
    text = """
    todo: Migrate user table
    action: Send weekly report
    This is just a comment about the weather.
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) >= 2
    assert any("migrate" in item.lower() for item in items)
    assert any("report" in item.lower() for item in items)


def test_llm_extract_empty_input():
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []
