"""Shared test fixtures for the HN MCP server tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from server.hn_client import HNClient
from server.models import CommentItem, StoryItem, UserProfile


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a test API key for all tests."""
    monkeypatch.setenv("HN_MCP_API_KEY", "test-secret-key")


@pytest.fixture()
def sample_story_data() -> dict:
    """Raw HN API story response data."""
    return {
        "id": 12345,
        "title": "Show HN: A New Project",
        "url": "https://example.com",
        "score": 150,
        "by": "testuser",
        "time": 1700000000,
        "descendants": 42,
        "type": "story",
        "kids": [100, 101, 102],
    }


@pytest.fixture()
def sample_comment_data() -> dict:
    """Raw HN API comment response data."""
    return {
        "id": 100,
        "text": "This is a great project!",
        "by": "commenter1",
        "time": 1700001000,
        "parent": 12345,
        "type": "comment",
        "kids": [200],
    }


@pytest.fixture()
def sample_user_data() -> dict:
    """Raw HN API user response data."""
    return {
        "id": "testuser",
        "created": 1500000000,
        "karma": 5000,
        "about": "I am a test user",
        "submitted": [12345, 12346, 12347],
    }


@pytest.fixture()
def sample_story(sample_story_data: dict) -> StoryItem:
    """Parsed StoryItem model."""
    return StoryItem.model_validate(sample_story_data)


@pytest.fixture()
def sample_comment(sample_comment_data: dict) -> CommentItem:
    """Parsed CommentItem model."""
    return CommentItem.model_validate(sample_comment_data)


@pytest.fixture()
def sample_user(sample_user_data: dict) -> UserProfile:
    """Parsed UserProfile model."""
    return UserProfile.model_validate(sample_user_data)


@pytest.fixture()
def mock_hn_client() -> AsyncMock:
    """A mocked HNClient for testing tools without network calls."""
    client = AsyncMock(spec=HNClient)
    return client
