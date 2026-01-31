"""
Investment Helper MCP Server - HTTP/SSE Transport

This module provides an HTTP server with Server-Sent Events (SSE) transport
for the MCP protocol. Use this for remote deployment (Railway, Render, etc.).

For local Claude Desktop usage, use main.py (STDIO transport) instead.

Usage:
    python -m server.http

Environment Variables:
    API_KEY: Required. Secret key for authenticating requests.
    PORT: Server port (default: 8000)
    HOST: Server host (default: 0.0.0.0)
    LOG_LEVEL: Logging level (default: INFO)
"""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
import uvicorn

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# Add parent directory to path for imports
_server_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_server_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from server.config import settings
from server.tools import get_market_briefing, analyze_ticker, get_crypto_analysis

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("investment-helper-http")

# Get API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.warning("API_KEY not set! Server will reject all authenticated requests.")


# =============================================================================
# Authentication
# =============================================================================


class APIKeyAuthBackend(AuthenticationBackend):
    """
    Bearer token authentication backend.

    Expects header: Authorization: Bearer <API_KEY>
    """

    async def authenticate(self, request: Request):
        # Skip auth for health check endpoint
        if request.url.path == "/health":
            return AuthCredentials(["public"]), SimpleUser("anonymous")

        if not API_KEY:
            raise AuthenticationError("Server API_KEY not configured")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationError("Missing Authorization header")

        try:
            scheme, token = auth_header.split(" ", 1)
        except ValueError:
            raise AuthenticationError("Invalid Authorization header format")

        if scheme.lower() != "bearer":
            raise AuthenticationError("Authorization scheme must be Bearer")

        if token != API_KEY:
            raise AuthenticationError("Invalid API key")

        return AuthCredentials(["authenticated"]), SimpleUser("api_client")


def auth_error_handler(request: Request, exc: AuthenticationError) -> Response:
    """Handle authentication errors with proper JSON response."""
    return JSONResponse(
        {"error": "authentication_failed", "message": str(exc)},
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"},
    )


# =============================================================================
# MCP Server Setup (same as main.py)
# =============================================================================

# Create the MCP server instance
mcp_server = Server("investment-helper")

# SSE transport instance (created per connection)
sse_transport = SseServerTransport("/messages")


@mcp_server.list_tools()
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


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
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


# =============================================================================
# HTTP Endpoints
# =============================================================================


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint (no auth required)."""
    return JSONResponse({
        "status": "healthy",
        "service": "investment-helper-mcp",
        "transport": "sse",
    })


async def handle_sse(request: Request) -> Response:
    """
    SSE endpoint for MCP client connections.

    The client connects here to receive server-sent events.
    Messages from client are sent to /messages endpoint.
    """
    logger.info(f"SSE connection from {request.client.host if request.client else 'unknown'}")

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options(),
        )

    return Response()


async def handle_messages(request: Request) -> Response:
    """
    Handle incoming MCP messages from clients.

    This endpoint receives POST requests with MCP protocol messages.
    """
    return await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


# =============================================================================
# Application Setup
# =============================================================================


@asynccontextmanager
async def lifespan(app: Starlette):
    """Application lifespan handler."""
    logger.info("Starting Investment Helper MCP Server (HTTP/SSE)")
    logger.info(f"API_KEY configured: {bool(API_KEY)}")
    yield
    logger.info("Shutting down Investment Helper MCP Server")


# Define routes
routes = [
    Route("/health", health_check, methods=["GET"]),
    Route("/sse", handle_sse, methods=["GET"]),
    Route("/messages", handle_messages, methods=["POST"]),
]

# Create Starlette app with authentication middleware
app = Starlette(
    routes=routes,
    lifespan=lifespan,
    middleware=[
        Middleware(
            AuthenticationMiddleware,
            backend=APIKeyAuthBackend(),
            on_error=auth_error_handler,
        ),
    ],
)


def main():
    """Entry point for HTTP server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
