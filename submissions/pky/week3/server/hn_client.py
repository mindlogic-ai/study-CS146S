"""Async HTTP client for the Hacker News Firebase API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from server.config import settings
from server.models import CommentItem, StoryItem, UserProfile

logger = logging.getLogger(__name__)

CATEGORY_MAP: dict[str, str] = {
    "top": "topstories",
    "new": "newstories",
    "best": "beststories",
    "ask": "askstories",
    "show": "showstories",
    "job": "jobstories",
}


class HNClient:
    """Async client for the Hacker News Firebase API.

    Uses connection pooling, concurrency limiting, and retry with backoff.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        max_concurrent: int | None = None,
    ) -> None:
        self.base_url = base_url or settings.hn_api_base_url
        self.timeout = timeout or settings.hn_api_timeout
        self.max_concurrent = max_concurrent or settings.hn_api_max_concurrent
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None

    async def start(self) -> None:
        """Initialize the HTTP client and semaphore."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not started."""
        if self._client is None:
            raise RuntimeError("HNClient not started. Call start() first.")
        return self._client

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """Get the semaphore, raising if not started."""
        if self._semaphore is None:
            raise RuntimeError("HNClient not started. Call start() first.")
        return self._semaphore

    async def _fetch_json(self, path: str, retries: int = 3) -> Any:
        """Fetch JSON from the HN API with retry and backoff.

        Args:
            path: API path (e.g., "/topstories.json")
            retries: Maximum number of retry attempts

        Returns:
            Parsed JSON response (dict, list, or None)
        """
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                async with self.semaphore:
                    response = await self.client.get(path)
                    response.raise_for_status()
                    text = response.text.strip()
                    if not text or text == "null":
                        return None
                    return response.json()
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                    raise
                wait = 2**attempt
                logger.warning(
                    "HN API request failed (attempt %d/%d): %s. Retrying in %ds...",
                    attempt + 1,
                    retries,
                    str(e),
                    wait,
                )
                await asyncio.sleep(wait)
        raise last_error or RuntimeError("Request failed after retries")

    async def fetch_story_ids(self, category: str = "top") -> list[int]:
        """Fetch story IDs for a given category.

        Args:
            category: One of "top", "new", "best", "ask", "show", "job"

        Returns:
            List of story IDs (up to 500)

        Raises:
            ValueError: If category is invalid
        """
        endpoint = CATEGORY_MAP.get(category)
        if not endpoint:
            valid = ", ".join(sorted(CATEGORY_MAP.keys()))
            raise ValueError(f"Invalid category '{category}'. Must be one of: {valid}")
        data = await self._fetch_json(f"/{endpoint}.json")
        return data if isinstance(data, list) else []

    async def fetch_item(self, item_id: int) -> dict[str, Any] | None:
        """Fetch a single item by ID.

        Returns None if the item doesn't exist or is deleted.
        """
        data = await self._fetch_json(f"/item/{item_id}.json")
        if data is None:
            return None
        if isinstance(data, dict) and data.get("deleted"):
            return None
        return data

    async def fetch_items_batch(self, item_ids: list[int]) -> list[dict[str, Any]]:
        """Fetch multiple items concurrently, filtering out None/deleted.

        Args:
            item_ids: List of item IDs to fetch

        Returns:
            List of valid item dicts (order not guaranteed, None items filtered)
        """
        tasks = [self.fetch_item(item_id) for item_id in item_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Failed to fetch item: %s", result)
                continue
            if result is not None:
                items.append(result)
        return items

    async def fetch_stories(self, category: str = "top", limit: int = 10) -> list[StoryItem]:
        """Fetch stories with full details.

        Args:
            category: Story category
            limit: Maximum number of stories (clamped to 1-30)

        Returns:
            List of StoryItem models
        """
        limit = max(1, min(30, limit))
        ids = await self.fetch_story_ids(category)
        ids = ids[:limit]
        raw_items = await self.fetch_items_batch(ids)
        stories: list[StoryItem] = []
        for item in raw_items:
            try:
                stories.append(StoryItem.model_validate(item))
            except Exception as e:
                logger.warning("Failed to parse story %s: %s", item.get("id"), e)
        stories.sort(key=lambda s: s.score, reverse=True)
        return stories

    async def fetch_story_details(self, story_id: int) -> StoryItem | None:
        """Fetch full details for a single story.

        Returns None if not found.
        """
        data = await self.fetch_item(story_id)
        if data is None:
            return None
        return StoryItem.model_validate(data)

    async def fetch_comments(self, kid_ids: list[int], limit: int = 5) -> list[CommentItem]:
        """Fetch comments by their IDs.

        Args:
            kid_ids: Comment IDs to fetch
            limit: Max comments to return (clamped to 1-20)

        Returns:
            List of CommentItem models (dead/deleted filtered out)
        """
        limit = max(1, min(20, limit))
        kid_ids = kid_ids[:limit]
        raw_items = await self.fetch_items_batch(kid_ids)
        comments: list[CommentItem] = []
        for item in raw_items:
            try:
                comment = CommentItem.model_validate(item)
                if not comment.dead:
                    comments.append(comment)
            except Exception as e:
                logger.warning("Failed to parse comment %s: %s", item.get("id"), e)
        return comments

    async def fetch_user(self, username: str) -> UserProfile | None:
        """Fetch a user profile by username.

        Returns None if user doesn't exist.
        """
        data = await self._fetch_json(f"/user/{username}.json")
        if data is None:
            return None
        return UserProfile.model_validate(data)

    async def search_stories(
        self, keyword: str, category: str = "top", limit: int = 10
    ) -> list[StoryItem]:
        """Search stories by keyword in title (client-side filtering).

        Fetches a window of stories and filters by case-insensitive title match.

        Args:
            keyword: Search term for title matching
            category: Which story list to search
            limit: Max results (clamped to 1-20)

        Returns:
            Matching stories
        """
        limit = max(1, min(20, limit))
        keyword_lower = keyword.lower()

        ids = await self.fetch_story_ids(category)
        scan_window = min(len(ids), 100)
        ids = ids[:scan_window]

        raw_items = await self.fetch_items_batch(ids)
        matches: list[StoryItem] = []
        for item in raw_items:
            try:
                story = StoryItem.model_validate(item)
                if keyword_lower in story.title.lower():
                    matches.append(story)
                    if len(matches) >= limit:
                        break
            except Exception as e:
                logger.warning("Failed to parse story %s: %s", item.get("id"), e)

        matches.sort(key=lambda s: s.score, reverse=True)
        return matches
