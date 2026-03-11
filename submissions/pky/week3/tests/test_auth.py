"""Tests for API key authentication."""

from __future__ import annotations

import pytest

from server.auth import ApiKeyVerifier


class TestApiKeyVerifier:
    """Tests for ApiKeyVerifier."""

    async def test_valid_key_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HN_MCP_API_KEY", "my-secret-key")
        verifier = ApiKeyVerifier()
        result = await verifier.verify_token("my-secret-key")
        assert result is not None
        assert result.token == "my-secret-key"

    async def test_invalid_key_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HN_MCP_API_KEY", "my-secret-key")
        verifier = ApiKeyVerifier()
        result = await verifier.verify_token("wrong-key")
        assert result is None

    async def test_no_key_configured_allows_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("HN_MCP_API_KEY", raising=False)
        verifier = ApiKeyVerifier()
        result = await verifier.verify_token("anything")
        assert result is not None
        assert result.scopes == ["read"]
