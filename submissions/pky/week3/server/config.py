"""Configuration for Hacker News MCP Server."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration loaded from environment variables."""

    hn_mcp_api_key: str = ""
    hn_api_base_url: str = "https://hacker-news.firebaseio.com/v0"
    hn_api_timeout: float = 10.0
    hn_api_max_concurrent: int = 30
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
