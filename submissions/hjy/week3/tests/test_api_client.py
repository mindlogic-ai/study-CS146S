"""
Test: API Client for BALLDONTLIE
Plan: /markdowns/mcp-nba-server.md
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from server.api_client import (
    BallDontLieClient,
    RateLimitError,
    APIError,
    RATE_LIMIT_REQUESTS,
)


class TestBallDontLieClient:
    """Test suite for BallDontLieClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = BallDontLieClient(api_key="test-api-key")

    def test_should_initialize_with_api_key(self):
        """Client should store the API key."""
        assert self.client.api_key == "test-api-key"

    def test_should_raise_rate_limit_error_when_limit_exceeded(self):
        """Client should raise RateLimitError when too many requests."""
        # Simulate hitting rate limit
        import time

        now = time.time()
        self.client._request_timestamps = [now] * RATE_LIMIT_REQUESTS

        with pytest.raises(RateLimitError) as exc_info:
            self.client._check_rate_limit()

        assert exc_info.value.retry_after > 0

    def test_should_clean_old_timestamps(self):
        """Client should remove timestamps older than the window."""
        import time

        # Add old timestamps (older than 60 seconds)
        old_time = time.time() - 120
        self.client._request_timestamps = [old_time] * 3

        # This should clean old timestamps and not raise
        self.client._check_rate_limit()
        assert len(self.client._request_timestamps) == 0

    @pytest.mark.asyncio
    async def test_should_parse_teams_response(self):
        """Client should correctly parse teams API response."""
        mock_response = {
            "data": [
                {
                    "id": 14,
                    "conference": "West",
                    "division": "Pacific",
                    "city": "Los Angeles",
                    "name": "Lakers",
                    "full_name": "Los Angeles Lakers",
                    "abbreviation": "LAL",
                }
            ]
        }

        with patch.object(self.client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            teams = await self.client.get_teams()

            assert len(teams) == 1
            assert teams[0]["full_name"] == "Los Angeles Lakers"
            assert teams[0]["abbreviation"] == "LAL"

    @pytest.mark.asyncio
    async def test_should_parse_players_response(self):
        """Client should correctly parse players API response."""
        mock_response = {
            "data": [
                {
                    "id": 237,
                    "first_name": "LeBron",
                    "last_name": "James",
                    "position": "F",
                    "height": "6-9",
                    "weight": "250",
                    "jersey_number": "23",
                    "team": {
                        "id": 14,
                        "full_name": "Los Angeles Lakers",
                    },
                }
            ]
        }

        with patch.object(self.client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            players = await self.client.search_players("LeBron")

            assert len(players) == 1
            assert players[0]["first_name"] == "LeBron"
            assert players[0]["last_name"] == "James"

    @pytest.mark.asyncio
    async def test_should_reject_short_search_query(self):
        """Client should reject search queries shorter than 2 characters."""
        with pytest.raises(APIError) as exc_info:
            await self.client.search_players("L")

        assert "at least 2 characters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_parse_games_response(self):
        """Client should correctly parse games API response."""
        mock_response = {
            "data": [
                {
                    "id": 1,
                    "date": "2025-01-15T00:00:00.000Z",
                    "season": 2024,
                    "status": "Final",
                    "home_team_score": 110,
                    "visitor_team_score": 105,
                    "home_team": {"id": 14, "full_name": "Los Angeles Lakers"},
                    "visitor_team": {"id": 2, "full_name": "Boston Celtics"},
                }
            ]
        }

        with patch.object(self.client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            games = await self.client.get_games(date="2025-01-15")

            assert len(games) == 1
            assert games[0]["status"] == "Final"
            assert games[0]["home_team_score"] == 110

    @pytest.mark.asyncio
    async def test_should_handle_timeout_error(self):
        """Client should handle timeout gracefully."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Connection timed out")

            with pytest.raises(APIError) as exc_info:
                await self.client._request("teams")

            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_handle_network_error(self):
        """Client should handle network errors gracefully."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Network unreachable")

            with pytest.raises(APIError) as exc_info:
                await self.client._request("teams")

            assert "Network error" in str(exc_info.value)
