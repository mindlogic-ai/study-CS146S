"""
Test: MCP Tools for NBA data
Plan: /markdowns/mcp-nba-server.md
"""

import pytest
from unittest.mock import AsyncMock, patch

from server.tools import (
    tool_get_teams,
    tool_search_player,
    tool_get_games,
    get_team_id,
    format_team,
    format_player,
    format_game,
)


class TestTeamIdMapping:
    """Test suite for team name to ID mapping."""

    def test_should_resolve_full_team_name(self):
        """Should resolve full team names to IDs."""
        assert get_team_id("Los Angeles Lakers") == 14
        assert get_team_id("Boston Celtics") == 2

    def test_should_resolve_short_team_name(self):
        """Should resolve short team names to IDs."""
        assert get_team_id("Lakers") == 14
        assert get_team_id("Celtics") == 2

    def test_should_resolve_abbreviation(self):
        """Should resolve team abbreviations to IDs."""
        assert get_team_id("LAL") == 14
        assert get_team_id("BOS") == 2

    def test_should_be_case_insensitive(self):
        """Should handle case insensitively."""
        assert get_team_id("lakers") == 14
        assert get_team_id("LAKERS") == 14
        assert get_team_id("LaKeRs") == 14

    def test_should_return_none_for_unknown_team(self):
        """Should return None for unknown teams."""
        assert get_team_id("Unknown Team") is None
        assert get_team_id("xyz") is None


class TestFormatters:
    """Test suite for data formatters."""

    def test_should_format_team(self):
        """Should format team data correctly."""
        team = {
            "full_name": "Los Angeles Lakers",
            "abbreviation": "LAL",
            "conference": "West",
            "division": "Pacific",
        }
        result = format_team(team)
        assert "Los Angeles Lakers" in result
        assert "LAL" in result
        assert "West" in result

    def test_should_format_player(self):
        """Should format player data correctly."""
        player = {
            "first_name": "LeBron",
            "last_name": "James",
            "position": "F",
            "height": "6-9",
            "weight": "250",
            "jersey_number": "23",
            "team": {"full_name": "Los Angeles Lakers"},
        }
        result = format_player(player)
        assert "LeBron James" in result
        assert "Los Angeles Lakers" in result
        assert "#23" in result

    def test_should_format_final_game(self):
        """Should format final game correctly."""
        game = {
            "date": "2025-01-15T00:00:00.000Z",
            "status": "Final",
            "home_team": {"full_name": "Los Angeles Lakers"},
            "visitor_team": {"full_name": "Boston Celtics"},
            "home_team_score": 110,
            "visitor_team_score": 105,
        }
        result = format_game(game)
        assert "Final" in result
        assert "110" in result
        assert "105" in result

    def test_should_format_scheduled_game(self):
        """Should format scheduled game correctly."""
        game = {
            "date": "2025-01-20T00:00:00.000Z",
            "status": "Scheduled",
            "home_team": {"full_name": "Los Angeles Lakers"},
            "visitor_team": {"full_name": "Boston Celtics"},
            "home_team_score": 0,
            "visitor_team_score": 0,
        }
        result = format_game(game)
        assert "Scheduled" in result


class TestToolGetTeams:
    """Test suite for get_teams tool."""

    @pytest.mark.asyncio
    async def test_should_return_all_teams(self):
        """Should return all teams when no filter provided."""
        mock_teams = [
            {"full_name": "Los Angeles Lakers", "abbreviation": "LAL", "conference": "West", "division": "Pacific"},
            {"full_name": "Boston Celtics", "abbreviation": "BOS", "conference": "East", "division": "Atlantic"},
        ]

        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_teams.return_value = mock_teams
            mock_get_client.return_value = mock_client

            result = await tool_get_teams()

            assert "Los Angeles Lakers" in result
            assert "Boston Celtics" in result

    @pytest.mark.asyncio
    async def test_should_filter_by_conference(self):
        """Should filter teams by conference."""
        mock_teams = [
            {"full_name": "Los Angeles Lakers", "abbreviation": "LAL", "conference": "West", "division": "Pacific"},
        ]

        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_teams.return_value = mock_teams
            mock_get_client.return_value = mock_client

            result = await tool_get_teams(conference="West")

            mock_client.get_teams.assert_called_once_with(conference="West")

    @pytest.mark.asyncio
    async def test_should_handle_empty_results(self):
        """Should handle empty results gracefully."""
        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_teams.return_value = []
            mock_get_client.return_value = mock_client

            result = await tool_get_teams()

            assert "No teams found" in result


class TestToolSearchPlayer:
    """Test suite for search_player tool."""

    @pytest.mark.asyncio
    async def test_should_search_players(self):
        """Should search for players by name."""
        mock_players = [
            {
                "first_name": "LeBron",
                "last_name": "James",
                "position": "F",
                "team": {"full_name": "Los Angeles Lakers"},
            }
        ]

        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.search_players.return_value = mock_players
            mock_get_client.return_value = mock_client

            result = await tool_search_player("LeBron")

            assert "LeBron James" in result

    @pytest.mark.asyncio
    async def test_should_reject_short_query(self):
        """Should reject search queries that are too short."""
        result = await tool_search_player("L")
        assert "at least 2 characters" in result

    @pytest.mark.asyncio
    async def test_should_handle_no_results(self):
        """Should handle no search results gracefully."""
        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.search_players.return_value = []
            mock_get_client.return_value = mock_client

            result = await tool_search_player("xyz123")

            assert "No players found" in result


class TestToolGetGames:
    """Test suite for get_games tool."""

    @pytest.mark.asyncio
    async def test_should_get_games_by_date(self):
        """Should get games for a specific date."""
        mock_games = [
            {
                "date": "2025-01-15T00:00:00.000Z",
                "status": "Final",
                "home_team": {"full_name": "Los Angeles Lakers"},
                "visitor_team": {"full_name": "Boston Celtics"},
                "home_team_score": 110,
                "visitor_team_score": 105,
            }
        ]

        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_games.return_value = mock_games
            mock_get_client.return_value = mock_client

            result = await tool_get_games(date="2025-01-15")

            assert "2025-01-15" in result
            assert "Final" in result

    @pytest.mark.asyncio
    async def test_should_get_games_by_team(self):
        """Should get games for a specific team."""
        mock_games = [
            {
                "date": "2025-01-15T00:00:00.000Z",
                "status": "Final",
                "home_team": {"full_name": "Los Angeles Lakers"},
                "visitor_team": {"full_name": "Boston Celtics"},
                "home_team_score": 110,
                "visitor_team_score": 105,
            }
        ]

        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_games.return_value = mock_games
            mock_get_client.return_value = mock_client

            result = await tool_get_games(team="Lakers")

            mock_client.get_games.assert_called_once_with(date=None, team_id=14)

    @pytest.mark.asyncio
    async def test_should_reject_unknown_team(self):
        """Should reject unknown team names."""
        result = await tool_get_games(team="Unknown Team XYZ")
        assert "Unknown team" in result

    @pytest.mark.asyncio
    async def test_should_handle_no_games(self):
        """Should handle no games found gracefully."""
        with patch("server.tools.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_games.return_value = []
            mock_get_client.return_value = mock_client

            result = await tool_get_games(date="2025-07-15")

            assert "No games found" in result
