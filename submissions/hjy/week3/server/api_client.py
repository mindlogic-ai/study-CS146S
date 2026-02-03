"""BALLDONTLIE API client with rate limiting and error handling."""

import asyncio
import time
from typing import Any

import httpx

from .config import (
    BALLDONTLIE_API_KEY,
    BALLDONTLIE_BASE_URL,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = RATE_LIMIT_WINDOW_SECONDS):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Please wait {retry_after} seconds.")


class APIError(Exception):
    """Raised when API returns an error."""

    pass


class BallDontLieClient:
    """Async client for BALLDONTLIE API with rate limiting."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or BALLDONTLIE_API_KEY
        self.base_url = BALLDONTLIE_BASE_URL
        self._request_timestamps: list[float] = []

    def _check_rate_limit(self) -> None:
        """Check if we're within rate limits, clean old timestamps."""
        now = time.time()
        # Remove timestamps older than the window
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < RATE_LIMIT_WINDOW_SECONDS
        ]
        if len(self._request_timestamps) >= RATE_LIMIT_REQUESTS:
            oldest = self._request_timestamps[0]
            retry_after = int(RATE_LIMIT_WINDOW_SECONDS - (now - oldest)) + 1
            raise RateLimitError(retry_after)

    def _record_request(self) -> None:
        """Record a request timestamp."""
        self._request_timestamps.append(time.time())

    async def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an authenticated request to the API."""
        self._check_rate_limit()

        headers = {"Authorization": self.api_key}
        url = f"{self.base_url}/{endpoint}"

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                self._record_request()

                if response.status_code == 429:
                    raise RateLimitError()
                elif response.status_code == 404:
                    raise APIError("Resource not found.")
                elif response.status_code >= 500:
                    raise APIError("API server error. Please try again later.")
                elif response.status_code >= 400:
                    raise APIError(f"API error: {response.text}")

                return response.json()

            except httpx.TimeoutException:
                raise APIError(f"Request timed out after {REQUEST_TIMEOUT_SECONDS} seconds.")
            except httpx.RequestError as e:
                raise APIError(f"Network error: {str(e)}")

    async def get_teams(self, conference: str | None = None) -> list[dict[str, Any]]:
        """Get all NBA teams, optionally filtered by conference."""
        params = {}
        if conference:
            params["conference"] = conference

        result = await self._request("teams", params if params else None)
        return result.get("data", [])

    async def get_team_by_id(self, team_id: int) -> dict[str, Any]:
        """Get a specific team by ID."""
        result = await self._request(f"teams/{team_id}")
        return result.get("data", {})

    async def search_players(self, name: str) -> list[dict[str, Any]]:
        """Search for players by name."""
        if not name or len(name.strip()) < 2:
            raise APIError("Search query must be at least 2 characters.")

        result = await self._request("players", {"search": name.strip()})
        return result.get("data", [])

    async def get_player_by_id(self, player_id: int) -> dict[str, Any]:
        """Get a specific player by ID."""
        result = await self._request(f"players/{player_id}")
        return result.get("data", {})

    async def get_games(
        self,
        date: str | None = None,
        team_id: int | None = None,
        season: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get games with optional filters."""
        params = {}
        if date:
            params["dates[]"] = date
        if team_id:
            params["team_ids[]"] = team_id
        if season:
            params["seasons[]"] = season

        result = await self._request("games", params if params else None)
        return result.get("data", [])

    async def get_game_by_id(self, game_id: int) -> dict[str, Any]:
        """Get a specific game by ID."""
        result = await self._request(f"games/{game_id}")
        return result.get("data", {})


# Singleton client instance
_client: BallDontLieClient | None = None


def get_client() -> BallDontLieClient:
    """Get or create the API client singleton."""
    global _client
    if _client is None:
        _client = BallDontLieClient()
    return _client
