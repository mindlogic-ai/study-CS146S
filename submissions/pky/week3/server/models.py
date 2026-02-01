"""Pydantic models for Hacker News API responses."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field, computed_field


class StoryItem(BaseModel):
    """A Hacker News story item."""

    id: int
    title: str = ""
    url: str | None = None
    score: int = 0
    by: str = ""
    time: int = 0
    descendants: int = 0
    type: str = "story"
    kids: list[int] = Field(default_factory=list)
    text: str | None = None
    deleted: bool = False
    dead: bool = False

    @computed_field
    @property
    def time_iso(self) -> str:
        """Convert Unix timestamp to ISO 8601 string."""
        if self.time == 0:
            return ""
        return datetime.fromtimestamp(self.time, tz=UTC).isoformat()

    @computed_field
    @property
    def comment_count(self) -> int:
        """Number of comments (alias for descendants)."""
        return self.descendants


class CommentItem(BaseModel):
    """A Hacker News comment item."""

    id: int
    text: str = ""
    by: str = ""
    time: int = 0
    parent: int = 0
    kids: list[int] = Field(default_factory=list)
    deleted: bool = False
    dead: bool = False
    type: str = "comment"

    @computed_field
    @property
    def time_iso(self) -> str:
        """Convert Unix timestamp to ISO 8601 string."""
        if self.time == 0:
            return ""
        return datetime.fromtimestamp(self.time, tz=UTC).isoformat()


class UserProfile(BaseModel):
    """A Hacker News user profile."""

    id: str
    created: int = 0
    karma: int = 0
    about: str | None = None
    submitted: list[int] = Field(default_factory=list)

    @computed_field
    @property
    def created_iso(self) -> str:
        """Convert Unix timestamp to ISO 8601 string."""
        if self.created == 0:
            return ""
        return datetime.fromtimestamp(self.created, tz=UTC).isoformat()

    @computed_field
    @property
    def submission_count(self) -> int:
        """Total number of submissions."""
        return len(self.submitted)
