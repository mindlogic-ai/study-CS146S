"""Hacker News MCP Server — main entrypoint."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.hn_client import HNClient
from server.tools import register_tools


def _setup_logging() -> None:
    """Configure logging to stderr (stdout is reserved for STDIO transport)."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Manage the HNClient lifecycle."""
    client = HNClient()
    await client.start()
    logging.getLogger(__name__).info("HN API client started")
    try:
        yield {"hn": client}
    finally:
        await client.close()
        logging.getLogger(__name__).info("HN API client closed")


def create_server(http_mode: bool = False) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        http_mode: If True, enable HTTP transport with API key auth.
                   If False, use STDIO transport (default).

    Returns:
        Configured FastMCP server instance.
    """
    kwargs: dict[str, Any] = {
        "name": "Hacker News MCP",
        "instructions": (
            "Access Hacker News stories, comments, and user profiles. "
            "Available tools: get_top_stories, get_story_details, "
            "get_user_profile, search_stories."
        ),
        "lifespan": app_lifespan,
    }

    if http_mode:
        from server.auth import ApiKeyVerifier

        kwargs["token_verifier"] = ApiKeyVerifier()
        kwargs["stateless_http"] = True
        kwargs["json_response"] = True

    mcp = FastMCP(**kwargs)
    register_tools(mcp)
    return mcp


def main() -> None:
    """Run the MCP server."""
    _setup_logging()
    logger = logging.getLogger(__name__)

    http_mode = "--http" in sys.argv
    transport = "streamable-http" if http_mode else "stdio"

    logger.info("Starting Hacker News MCP server (transport=%s)", transport)
    server = create_server(http_mode=http_mode)
    server.run(transport=transport)


if __name__ == "__main__":
    main()
