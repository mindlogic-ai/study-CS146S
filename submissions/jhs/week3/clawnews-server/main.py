"""ClawNews MCP Server - Fetch AI agent news from ClawNews.io."""

import logging
from typing import Optional

import httpx
from fastmcp import FastMCP

# Configure logging (stderr only for STDIO transport)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ClawNews API base URL
BASE_URL = "https://clawnews.io"

# Initialize FastMCP server
mcp = FastMCP(
    name="clawnews-mcp",
    instructions="Fetch AI agent news from ClawNews.io. Get top stories, daily digests, or specific story details.",
)

# HTTP client with timeout and retry settings
_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=30.0,
            headers={"User-Agent": "ClawNews-MCP-Server/0.1.0"},
        )
    return _client


@mcp.tool()
async def get_top_stories(limit: int = 10) -> dict:
    """
    Fetch top stories from ClawNews.

    Args:
        limit: Number of stories to return (default 10, max 30)

    Returns:
        Dictionary containing list of top stories with titles, scores, URLs, and metadata.
    """
    try:
        limit = min(max(1, limit), 30)  # Clamp between 1 and 30
        client = await get_client()

        # Get top story IDs
        response = await client.get("/topstories.json")
        response.raise_for_status()
        story_ids = response.json()[:limit]

        if not story_ids:
            return {"stories": [], "count": 0, "message": "No stories found"}

        # Fetch each story's details
        stories = []
        for story_id in story_ids:
            try:
                item_response = await client.get(f"/item/{story_id}")
                item_response.raise_for_status()
                item = item_response.json()

                stories.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "score": item.get("score", 0),
                    "by": item.get("by"),
                    "time": item.get("time"),
                    "comment_count": len(item.get("kids", [])),
                    "type": item.get("type"),
                })
            except httpx.HTTPError as e:
                logger.warning(f"Failed to fetch story {story_id}: {e}")
                continue

        return {
            "stories": stories,
            "count": len(stories),
            "source": "clawnews.io",
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        if e.response.status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later."}
        return {"error": f"HTTP error: {e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return {"error": f"Failed to connect to ClawNews: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def get_digest(date: Optional[str] = None) -> dict:
    """
    Fetch the daily digest from ClawNews.

    Args:
        date: Optional date in YYYY-MM-DD format. If not provided, returns today's digest.

    Returns:
        Dictionary containing the digest with curated stories and summaries.
    """
    try:
        client = await get_client()

        # Build endpoint
        if date:
            endpoint = f"/digest/{date}.json"
        else:
            endpoint = "/digest.json"

        response = await client.get(endpoint)
        response.raise_for_status()
        digest = response.json()

        return {
            "date": digest.get("date", date or "today"),
            "title": digest.get("title"),
            "summary": digest.get("summary"),
            "stories": digest.get("stories", []),
            "story_count": len(digest.get("stories", [])),
            "source": "clawnews.io",
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        if e.response.status_code == 404:
            return {"error": f"Digest not found for date: {date or 'today'}"}
        if e.response.status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later."}
        return {"error": f"HTTP error: {e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return {"error": f"Failed to connect to ClawNews: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def get_story(story_id: int) -> dict:
    """
    Fetch a specific story with its comments from ClawNews.

    Args:
        story_id: The numeric ID of the story to fetch

    Returns:
        Dictionary containing story details and top-level comments.
    """
    try:
        client = await get_client()

        response = await client.get(f"/item/{story_id}")
        response.raise_for_status()
        item = response.json()

        if not item:
            return {"error": f"Story not found: {story_id}"}

        # Fetch top-level comments (limit to first 5 for brevity)
        comments = []
        kids = item.get("kids", [])[:5]
        for comment_id in kids:
            try:
                comment_response = await client.get(f"/item/{comment_id}")
                comment_response.raise_for_status()
                comment = comment_response.json()
                comments.append({
                    "id": comment.get("id"),
                    "by": comment.get("by"),
                    "text": comment.get("text"),
                    "time": comment.get("time"),
                })
            except httpx.HTTPError:
                continue

        return {
            "id": item.get("id"),
            "type": item.get("type"),
            "title": item.get("title"),
            "url": item.get("url"),
            "text": item.get("text"),
            "by": item.get("by"),
            "time": item.get("time"),
            "score": item.get("score", 0),
            "comment_count": len(item.get("kids", [])),
            "comments": comments,
            "source": "clawnews.io",
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        if e.response.status_code == 404:
            return {"error": f"Story not found: {story_id}"}
        if e.response.status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later."}
        return {"error": f"HTTP error: {e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return {"error": f"Failed to connect to ClawNews: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
