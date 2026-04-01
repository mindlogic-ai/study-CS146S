"""Simple in-memory rate limiter for API calls."""

import time
import asyncio
from .errors import RateLimitError


class RateLimiter:
    """
    Simple rate limiter that tracks calls within a sliding window.

    Raises RateLimitError if too many calls are made within the window.
    """

    def __init__(self, calls_per_minute: int):
        """
        Initialize the rate limiter.

        Args:
            calls_per_minute: Maximum number of calls allowed per minute.
        """
        self.calls_per_minute = calls_per_minute
        self.calls: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make an API call.

        Raises:
            RateLimitError: If rate limit is exceeded.
        """
        async with self._lock:
            now = time.time()
            # Remove calls older than 60 seconds
            self.calls = [t for t in self.calls if now - t < 60]

            if len(self.calls) >= self.calls_per_minute:
                wait_time = 60 - (now - self.calls[0])
                raise RateLimitError(
                    f"Rate limited. Try again in {wait_time:.0f} seconds.",
                    wait_seconds=wait_time,
                )

            self.calls.append(now)

    async def wait_and_acquire(self) -> None:
        """
        Wait if necessary, then acquire permission to make an API call.

        This method will block until a slot is available rather than raising an error.
        """
        async with self._lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < 60]

            if len(self.calls) >= self.calls_per_minute:
                wait_time = 60 - (now - self.calls[0]) + 0.1
                await asyncio.sleep(wait_time)
                now = time.time()
                self.calls = [t for t in self.calls if now - t < 60]

            self.calls.append(now)

    def reset(self) -> None:
        """Reset the rate limiter, clearing all tracked calls."""
        self.calls = []
