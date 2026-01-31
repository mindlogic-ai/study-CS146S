"""Configuration settings for the Investment Helper MCP server."""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    """Server configuration settings."""

    log_level: str = "INFO"
    coingecko_rate_limit: int = 10
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    request_timeout: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            coingecko_rate_limit=int(os.getenv("COINGECKO_RATE_LIMIT", "10")),
        )


settings = Settings.from_env()
