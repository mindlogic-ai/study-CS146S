"""MCP tool definitions for the Hacker News server."""

from __future__ import annotations

import json
import logging

from mcp.server.fastmcp import Context, FastMCP

from server.hn_client import CATEGORY_MAP, HNClient

logger = logging.getLogger(__name__)


def _get_hn_client(ctx: Context) -> HNClient:
    """Extract the HNClient from the request context."""
    return ctx.request_context.lifespan_context["hn"]


def register_tools(mcp: FastMCP) -> None:
    """Register all HN tools on the given FastMCP server instance."""

    @mcp.tool()
    async def get_top_stories(
        category: str = "top",
        limit: int = 10,
        ctx: Context = None,
    ) -> str:
        """Fetch top/new/best/ask/show/job stories from Hacker News.

        Args:
            category: Story category. One of: top, new, best, ask, show, job.
            limit: Maximum number of stories to return (1-30). Defaults to 10.
        """
        valid_categories = sorted(CATEGORY_MAP.keys())
        if category not in CATEGORY_MAP:
            return json.dumps(
                {"error": "invalid_category", "message": f"Must be one of: {valid_categories}"},
                indent=2,
            )

        hn = _get_hn_client(ctx)
        try:
            stories = await hn.fetch_stories(category=category, limit=limit)
            result = [
                {
                    "id": s.id,
                    "title": s.title,
                    "url": s.url,
                    "score": s.score,
                    "author": s.by,
                    "time": s.time_iso,
                    "comment_count": s.comment_count,
                }
                for s in stories
            ]
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error("Error fetching stories: %s", e)
            return json.dumps({"error": "fetch_failed", "message": str(e)}, indent=2)

    @mcp.tool()
    async def get_story_details(
        story_id: int,
        include_comments: bool = False,
        comment_limit: int = 5,
        ctx: Context = None,
    ) -> str:
        """Get full details of a Hacker News story by its ID.

        Args:
            story_id: The numeric Hacker News item ID.
            include_comments: Whether to fetch top-level comments. Defaults to False.
            comment_limit: Max comments to include (1-20). Defaults to 5.
        """
        if story_id <= 0:
            return json.dumps(
                {"error": "invalid_id", "message": "story_id must be a positive integer"},
                indent=2,
            )

        hn = _get_hn_client(ctx)
        try:
            story = await hn.fetch_story_details(story_id)
            if story is None:
                return json.dumps(
                    {"error": "not_found", "message": f"Story {story_id} not found"},
                    indent=2,
                )

            result: dict = {
                "id": story.id,
                "title": story.title,
                "url": story.url,
                "text": story.text,
                "score": story.score,
                "author": story.by,
                "time": story.time_iso,
                "comment_count": story.comment_count,
                "type": story.type,
            }

            if include_comments and story.kids:
                comments = await hn.fetch_comments(story.kids, limit=comment_limit)
                result["comments"] = [
                    {
                        "id": c.id,
                        "text": c.text,
                        "author": c.by,
                        "time": c.time_iso,
                    }
                    for c in comments
                ]

            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error("Error fetching story details: %s", e)
            return json.dumps({"error": "fetch_failed", "message": str(e)}, indent=2)

    @mcp.tool()
    async def get_user_profile(
        username: str,
        ctx: Context = None,
    ) -> str:
        """Get a Hacker News user's profile information.

        Args:
            username: The HN username (case-sensitive).
        """
        if not username or not username.strip():
            return json.dumps(
                {"error": "invalid_username", "message": "Username cannot be empty"},
                indent=2,
            )

        hn = _get_hn_client(ctx)
        try:
            user = await hn.fetch_user(username.strip())
            if user is None:
                return json.dumps(
                    {"error": "not_found", "message": f"User '{username}' not found"},
                    indent=2,
                )

            return json.dumps(
                {
                    "id": user.id,
                    "karma": user.karma,
                    "created": user.created_iso,
                    "about": user.about,
                    "submission_count": user.submission_count,
                },
                indent=2,
            )
        except Exception as e:
            logger.error("Error fetching user profile: %s", e)
            return json.dumps({"error": "fetch_failed", "message": str(e)}, indent=2)

    @mcp.tool()
    async def search_stories(
        keyword: str,
        category: str = "top",
        limit: int = 10,
        ctx: Context = None,
    ) -> str:
        """Search recent Hacker News stories by keyword in title.

        Fetches recent stories and filters by case-insensitive keyword match in titles.
        Note: This is client-side filtering since the HN API has no search endpoint.

        Args:
            keyword: Search term to match against story titles (case-insensitive).
            category: Which story list to search. One of: top, new, best. Defaults to top.
            limit: Maximum results to return (1-20). Defaults to 10.
        """
        if not keyword or not keyword.strip():
            return json.dumps(
                {"error": "invalid_keyword", "message": "Keyword cannot be empty"},
                indent=2,
            )

        valid_categories = ["top", "new", "best"]
        if category not in valid_categories:
            return json.dumps(
                {
                    "error": "invalid_category",
                    "message": f"Must be one of: {valid_categories}",
                },
                indent=2,
            )

        hn = _get_hn_client(ctx)
        try:
            stories = await hn.search_stories(
                keyword=keyword.strip(), category=category, limit=limit
            )
            result = [
                {
                    "id": s.id,
                    "title": s.title,
                    "url": s.url,
                    "score": s.score,
                    "author": s.by,
                    "time": s.time_iso,
                    "comment_count": s.comment_count,
                }
                for s in stories
            ]
            return json.dumps(
                {"keyword": keyword.strip(), "count": len(result), "stories": result},
                indent=2,
            )
        except Exception as e:
            logger.error("Error searching stories: %s", e)
            return json.dumps({"error": "search_failed", "message": str(e)}, indent=2)
