"""Tests for the HN API client."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from server.hn_client import HNClient


@pytest.fixture()
async def hn_client() -> HNClient:
    """Create an HNClient for testing."""
    client = HNClient(
        base_url="https://hacker-news.firebaseio.com/v0",
        timeout=5.0,
        max_concurrent=5,
    )
    await client.start()
    yield client
    await client.close()


class TestFetchStoryIds:
    """Tests for fetch_story_ids."""

    @respx.mock
    async def test_fetch_top_stories(self, hn_client: HNClient) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
            return_value=Response(200, json=[1, 2, 3, 4, 5])
        )
        ids = await hn_client.fetch_story_ids("top")
        assert ids == [1, 2, 3, 4, 5]

    @respx.mock
    async def test_fetch_new_stories(self, hn_client: HNClient) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/newstories.json").mock(
            return_value=Response(200, json=[10, 20, 30])
        )
        ids = await hn_client.fetch_story_ids("new")
        assert ids == [10, 20, 30]

    async def test_invalid_category(self, hn_client: HNClient) -> None:
        with pytest.raises(ValueError, match="Invalid category"):
            await hn_client.fetch_story_ids("invalid")


class TestFetchItem:
    """Tests for fetch_item."""

    @respx.mock
    async def test_fetch_existing_item(self, hn_client: HNClient, sample_story_data: dict) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/item/12345.json").mock(
            return_value=Response(200, json=sample_story_data)
        )
        item = await hn_client.fetch_item(12345)
        assert item is not None
        assert item["id"] == 12345

    @respx.mock
    async def test_fetch_nonexistent_item(self, hn_client: HNClient) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/item/99999.json").mock(
            return_value=Response(200, json=None)
        )
        item = await hn_client.fetch_item(99999)
        assert item is None

    @respx.mock
    async def test_fetch_deleted_item(self, hn_client: HNClient) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/item/11111.json").mock(
            return_value=Response(200, json={"id": 11111, "deleted": True})
        )
        item = await hn_client.fetch_item(11111)
        assert item is None


class TestFetchUser:
    """Tests for fetch_user."""

    @respx.mock
    async def test_fetch_existing_user(self, hn_client: HNClient, sample_user_data: dict) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/user/testuser.json").mock(
            return_value=Response(200, json=sample_user_data)
        )
        user = await hn_client.fetch_user("testuser")
        assert user is not None
        assert user.id == "testuser"
        assert user.karma == 5000

    @respx.mock
    async def test_fetch_nonexistent_user(self, hn_client: HNClient) -> None:
        respx.get("https://hacker-news.firebaseio.com/v0/user/nobody.json").mock(
            return_value=Response(200, json=None)
        )
        user = await hn_client.fetch_user("nobody")
        assert user is None


class TestModels:
    """Tests for Pydantic model parsing."""

    def test_story_with_missing_fields(self) -> None:
        """Stories should handle missing optional fields gracefully."""
        from server.models import StoryItem

        story = StoryItem.model_validate({"id": 1})
        assert story.id == 1
        assert story.title == ""
        assert story.url is None
        assert story.score == 0
        assert story.kids == []

    def test_story_time_iso(self, sample_story_data: dict) -> None:
        from server.models import StoryItem

        story = StoryItem.model_validate(sample_story_data)
        assert story.time_iso != ""
        assert "2023" in story.time_iso or "2024" in story.time_iso

    def test_user_submission_count(self, sample_user_data: dict) -> None:
        from server.models import UserProfile

        user = UserProfile.model_validate(sample_user_data)
        assert user.submission_count == 3

    def test_comment_deleted_flag(self) -> None:
        from server.models import CommentItem

        comment = CommentItem.model_validate({"id": 1, "deleted": True})
        assert comment.deleted is True
