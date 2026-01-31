"""Custom exceptions and error handling for the MCP server."""

from pydantic import BaseModel


class ToolError(BaseModel):
    """Structured error response for tool failures."""

    error: bool = True
    message: str
    suggestion: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"error": self.error, "message": self.message}
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, wait_seconds: float = 0):
        self.message = message
        self.wait_seconds = wait_seconds
        super().__init__(message)


class InvalidSymbolError(Exception):
    """Raised when a stock/crypto symbol is invalid or not found."""

    def __init__(self, symbol: str, asset_type: str = "asset"):
        self.symbol = symbol
        self.asset_type = asset_type
        self.message = f"Invalid {asset_type} symbol: {symbol}"
        super().__init__(self.message)


class APIError(Exception):
    """Raised when an external API call fails."""

    def __init__(self, api_name: str, status_code: int | None = None, message: str = ""):
        self.api_name = api_name
        self.status_code = status_code
        self.message = message or f"API error from {api_name}"
        if status_code:
            self.message += f" (status: {status_code})"
        super().__init__(self.message)
