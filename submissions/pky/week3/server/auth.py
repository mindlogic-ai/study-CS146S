"""API key authentication for the Hacker News MCP Server."""

from __future__ import annotations

import logging
import os

from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)


class ApiKeyVerifier(TokenVerifier):
    """Validates requests against the HN_MCP_API_KEY environment variable.

    If HN_MCP_API_KEY is not set, all requests are allowed (development mode).
    For production, set the environment variable to a secure random string.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify an API key token.

        Args:
            token: The Bearer token from the Authorization header.

        Returns:
            AccessToken if valid, None if rejected.
        """
        expected = os.environ.get("HN_MCP_API_KEY", "")
        if not expected:
            logger.warning("HN_MCP_API_KEY not set — auth disabled (dev mode)")
            return AccessToken(token=token, client_id="dev", scopes=["read"], expires_at=None)
        if token == expected:
            return AccessToken(token=token, client_id="api-key", scopes=["read"], expires_at=None)
        logger.warning("Invalid API key attempt")
        return None
