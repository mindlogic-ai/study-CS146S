"""MCP NBA Server - Main entry point."""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import tool_get_teams, tool_search_player, tool_get_games

# Configure logging to stderr (important for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp-nba")

# Create server instance
server = Server("mcp-nba")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_teams",
            description="Get NBA teams list, optionally filtered by conference (East/West). Returns team names, abbreviations, and divisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "conference": {
                        "type": "string",
                        "description": "Filter by conference: 'East' or 'West'. Leave empty for all teams.",
                        "enum": ["East", "West"],
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="search_player",
            description="Search for NBA players by name. Returns player info including team, position, height, and weight.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Player name to search for (e.g., 'LeBron', 'Curry', 'Jokic'). Minimum 2 characters.",
                        "minLength": 2,
                    }
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="get_games",
            description="Get NBA games, optionally filtered by date and/or team. Returns game scores and status (scheduled, live, or final).",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Game date in YYYY-MM-DD format (e.g., '2025-01-15').",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    },
                    "team": {
                        "type": "string",
                        "description": "Team name, city, or abbreviation (e.g., 'Lakers', 'LAL', 'Los Angeles Lakers').",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        if name == "get_teams":
            result = await tool_get_teams(conference=arguments.get("conference"))
        elif name == "search_player":
            result = await tool_search_player(name=arguments.get("name", ""))
        elif name == "get_games":
            result = await tool_get_games(
                date=arguments.get("date"),
                team=arguments.get("team"),
            )
        else:
            result = f"Unknown tool: {name}"

        logger.info(f"Tool {name} completed successfully")
        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Tool {name} failed: {str(e)}")
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting MCP NBA Server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
