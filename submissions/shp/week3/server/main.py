"""
Investment Helper MCP Server

A Model Context Protocol server for investment decision-making that aggregates
stock prices, crypto data, and market trends using free APIs.

IMPORTANT: This server uses STDIO transport. All logging goes to stderr.
"""

import asyncio
import json
import logging
import os
import sys

# Add the parent directory to sys.path so imports work when run directly
_server_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_server_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from server.config import settings
from server.tools import get_market_briefing, analyze_ticker, get_crypto_analysis

# CRITICAL: Configure logging to stderr only (stdout breaks STDIO transport)
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("investment-helper")

# Create the MCP server instance
server = Server("investment-helper")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools in this MCP server."""
    return [
        Tool(
            name="get_market_briefing",
            description=(
                "Get a morning briefing of stock indices and crypto market overview. "
                "Returns major index prices (S&P 500, NASDAQ, Dow Jones), market status, "
                "Bitcoin/Ethereum prices, and trending cryptocurrencies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "include_crypto": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include cryptocurrency summary in the briefing",
                    },
                    "indices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["^GSPC", "^IXIC", "^DJI"],
                        "description": (
                            "Index symbols to include. Common: "
                            "^GSPC (S&P 500), ^IXIC (NASDAQ), ^DJI (Dow Jones)"
                        ),
                    },
                },
            },
        ),
        Tool(
            name="analyze_ticker",
            description=(
                "Get detailed analysis of a stock ticker. Returns current price, "
                "daily change, 52-week range, volume, market cap, P/E ratio, "
                "sector, company description, and 5-day price trend."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": (
                            "Stock ticker symbol (e.g., NVDA, AAPL, TSLA, MSFT). "
                            "Use uppercase letters."
                        ),
                    },
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="get_crypto_analysis",
            description=(
                "Get detailed analysis of a cryptocurrency. Returns current price, "
                "24h/7d/30d price changes, market cap and rank, all-time high/low, "
                "supply information, community sentiment, and investment insights."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "coin_id": {
                        "type": "string",
                        "description": (
                            "CoinGecko coin ID (e.g., bitcoin, ethereum, solana). "
                            "Use lowercase. Find IDs at coingecko.com."
                        ),
                    },
                },
                "required": ["coin_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.

    Args:
        name: The name of the tool to call.
        arguments: Dictionary of arguments passed to the tool.

    Returns:
        List containing a single TextContent with JSON-formatted result.
    """
    logger.info(f"Tool called: {name} with args: {arguments}")

    try:
        if name == "get_market_briefing":
            result = await get_market_briefing(
                include_crypto=arguments.get("include_crypto", True),
                indices=arguments.get("indices"),
            )
        elif name == "analyze_ticker":
            symbol = arguments.get("symbol", "")
            if not symbol:
                result = {
                    "error": True,
                    "message": "Missing required parameter: symbol",
                    "suggestion": "Provide a stock symbol like NVDA, AAPL, or TSLA",
                }
            else:
                result = await analyze_ticker(symbol)
        elif name == "get_crypto_analysis":
            coin_id = arguments.get("coin_id", "")
            if not coin_id:
                result = {
                    "error": True,
                    "message": "Missing required parameter: coin_id",
                    "suggestion": "Provide a CoinGecko ID like bitcoin, ethereum, or solana",
                }
            else:
                result = await get_crypto_analysis(coin_id)
        else:
            result = {
                "error": True,
                "message": f"Unknown tool: {name}",
                "suggestion": "Available tools: get_market_briefing, analyze_ticker, get_crypto_analysis",
            }

        logger.info(f"Tool {name} completed successfully")
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        logger.error(f"Tool error in {name}: {e}", exc_info=True)
        error_response = {
            "error": True,
            "message": f"Internal error: {str(e)}",
            "suggestion": "Please try again. If the issue persists, check the logs.",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Investment Helper MCP Server")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"CoinGecko rate limit: {settings.coingecko_rate_limit} calls/min")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run():
    """Entry point for running the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
