"""MCP tool definitions for NBA data."""

from .api_client import get_client, APIError, RateLimitError


def format_team(team: dict) -> str:
    """Format team data for display."""
    return f"{team.get('full_name', 'Unknown')} ({team.get('abbreviation', '?')}) - {team.get('conference', '?')} Conference, {team.get('division', '?')} Division"


def format_player(player: dict) -> str:
    """Format player data for display."""
    team = player.get("team", {})
    team_name = team.get("full_name", "Unknown Team") if team else "Unknown Team"

    height = ""
    if player.get("height"):
        height = f", Height: {player['height']}"

    weight = ""
    if player.get("weight"):
        weight = f", Weight: {player['weight']} lbs"

    position = ""
    if player.get("position"):
        position = f", Position: {player['position']}"

    jersey = ""
    if player.get("jersey_number"):
        jersey = f", #{player['jersey_number']}"

    return f"{player.get('first_name', '')} {player.get('last_name', '')} - {team_name}{jersey}{position}{height}{weight}"


def format_game(game: dict) -> str:
    """Format game data for display."""
    home_team = game.get("home_team", {})
    visitor_team = game.get("visitor_team", {})

    home_name = home_team.get("full_name", "Unknown")
    visitor_name = visitor_team.get("full_name", "Unknown")
    home_score = game.get("home_team_score", 0)
    visitor_score = game.get("visitor_team_score", 0)

    date = game.get("date", "Unknown date")[:10]  # YYYY-MM-DD
    status = game.get("status", "Unknown")

    if status == "Final":
        result = f"Final: {visitor_name} {visitor_score} @ {home_name} {home_score}"
    elif status in ("In Progress", "1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "Halftime"):
        result = f"LIVE ({status}): {visitor_name} {visitor_score} @ {home_name} {home_score}"
    else:
        result = f"Scheduled: {visitor_name} @ {home_name}"

    return f"[{date}] {result}"


# Team name to ID mapping (commonly searched teams)
TEAM_NAME_MAP = {
    # Full names
    "atlanta hawks": 1, "boston celtics": 2, "brooklyn nets": 3, "charlotte hornets": 4,
    "chicago bulls": 5, "cleveland cavaliers": 6, "dallas mavericks": 7, "denver nuggets": 8,
    "detroit pistons": 9, "golden state warriors": 10, "houston rockets": 11, "indiana pacers": 12,
    "los angeles clippers": 13, "los angeles lakers": 14, "memphis grizzlies": 15,
    "miami heat": 16, "milwaukee bucks": 17, "minnesota timberwolves": 18,
    "new orleans pelicans": 19, "new york knicks": 20, "oklahoma city thunder": 21,
    "orlando magic": 22, "philadelphia 76ers": 23, "phoenix suns": 24, "portland trail blazers": 25,
    "sacramento kings": 26, "san antonio spurs": 27, "toronto raptors": 28, "utah jazz": 29,
    "washington wizards": 30,
    # Short names
    "hawks": 1, "celtics": 2, "nets": 3, "hornets": 4, "bulls": 5, "cavaliers": 6, "cavs": 6,
    "mavericks": 7, "mavs": 7, "nuggets": 8, "pistons": 9, "warriors": 10, "dubs": 10,
    "rockets": 11, "pacers": 12, "clippers": 13, "lakers": 14, "grizzlies": 15, "heat": 16,
    "bucks": 17, "timberwolves": 18, "wolves": 18, "pelicans": 19, "pels": 19, "knicks": 20,
    "thunder": 21, "okc": 21, "magic": 22, "sixers": 23, "76ers": 23, "suns": 24,
    "trail blazers": 25, "blazers": 25, "kings": 26, "spurs": 27, "raptors": 28, "jazz": 29,
    "wizards": 30,
    # Abbreviations
    "atl": 1, "bos": 2, "bkn": 3, "cha": 4, "chi": 5, "cle": 6, "dal": 7, "den": 8,
    "det": 9, "gsw": 10, "hou": 11, "ind": 12, "lac": 13, "lal": 14, "mem": 15,
    "mia": 16, "mil": 17, "min": 18, "nop": 19, "nyk": 20, "okc": 21, "orl": 22,
    "phi": 23, "phx": 24, "por": 25, "sac": 26, "sas": 27, "tor": 28, "uta": 29, "was": 30,
}


def get_team_id(team_name: str) -> int | None:
    """Get team ID from team name or abbreviation."""
    return TEAM_NAME_MAP.get(team_name.lower().strip())


async def tool_get_teams(conference: str | None = None) -> str:
    """
    Get NBA teams, optionally filtered by conference.

    Args:
        conference: Filter by conference ("East" or "West"). If not provided, returns all teams.

    Returns:
        Formatted list of NBA teams.
    """
    try:
        client = get_client()
        teams = await client.get_teams(conference=conference)

        if not teams:
            return "No teams found."

        lines = [f"NBA Teams ({len(teams)} total):"]
        lines.append("")

        # Group by conference
        east_teams = [t for t in teams if t.get("conference") == "East"]
        west_teams = [t for t in teams if t.get("conference") == "West"]

        if east_teams and (not conference or conference.lower() == "east"):
            lines.append("=== Eastern Conference ===")
            for team in sorted(east_teams, key=lambda t: t.get("division", "")):
                lines.append(f"  {format_team(team)}")
            lines.append("")

        if west_teams and (not conference or conference.lower() == "west"):
            lines.append("=== Western Conference ===")
            for team in sorted(west_teams, key=lambda t: t.get("division", "")):
                lines.append(f"  {format_team(team)}")

        return "\n".join(lines)

    except RateLimitError as e:
        return f"Rate limit exceeded. Please wait {e.retry_after} seconds before trying again."
    except APIError as e:
        return f"Error: {str(e)}"


async def tool_search_player(name: str) -> str:
    """
    Search for NBA players by name.

    Args:
        name: Player name to search for (e.g., "LeBron", "Curry", "Jokic").
              Must be at least 2 characters.

    Returns:
        Formatted list of matching players with their team and stats.
    """
    if not name or len(name.strip()) < 2:
        return "Please provide a search term with at least 2 characters."

    try:
        client = get_client()
        players = await client.search_players(name)

        if not players:
            return f"No players found matching '{name}'."

        lines = [f"Players matching '{name}' ({len(players)} found):"]
        lines.append("")

        for player in players[:10]:  # Limit to 10 results
            lines.append(f"  • {format_player(player)}")

        if len(players) > 10:
            lines.append(f"\n  ... and {len(players) - 10} more results.")

        return "\n".join(lines)

    except RateLimitError as e:
        return f"Rate limit exceeded. Please wait {e.retry_after} seconds before trying again."
    except APIError as e:
        return f"Error: {str(e)}"


async def tool_get_games(date: str | None = None, team: str | None = None) -> str:
    """
    Get NBA games, optionally filtered by date and/or team.

    Args:
        date: Game date in YYYY-MM-DD format (e.g., "2025-01-15").
              If not provided, returns recent games.
        team: Team name, city, or abbreviation (e.g., "Lakers", "LAL", "Los Angeles Lakers").
              If not provided, returns all games for the date.

    Returns:
        Formatted list of games with scores and status.
    """
    try:
        client = get_client()

        team_id = None
        if team:
            team_id = get_team_id(team)
            if team_id is None:
                return f"Unknown team '{team}'. Try using the full team name (e.g., 'Los Angeles Lakers'), city name (e.g., 'Lakers'), or abbreviation (e.g., 'LAL')."

        games = await client.get_games(date=date, team_id=team_id)

        if not games:
            filter_desc = []
            if date:
                filter_desc.append(f"date {date}")
            if team:
                filter_desc.append(f"team {team}")
            filter_str = " and ".join(filter_desc) if filter_desc else "the given criteria"
            return f"No games found for {filter_str}."

        # Build header
        header_parts = ["NBA Games"]
        if date:
            header_parts.append(f"on {date}")
        if team:
            header_parts.append(f"for {team}")
        header = " ".join(header_parts)

        lines = [f"{header} ({len(games)} games):"]
        lines.append("")

        for game in games[:15]:  # Limit to 15 games
            lines.append(f"  • {format_game(game)}")

        if len(games) > 15:
            lines.append(f"\n  ... and {len(games) - 15} more games.")

        return "\n".join(lines)

    except RateLimitError as e:
        return f"Rate limit exceeded. Please wait {e.retry_after} seconds before trying again."
    except APIError as e:
        return f"Error: {str(e)}"
