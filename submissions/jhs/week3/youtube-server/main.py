"""YouTube MCP Server - Fetch video metadata and transcripts."""

import os
import re
import logging
from typing import Optional

from fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

# Configure logging (stderr only for STDIO transport)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="youtube-mcp",
    instructions="Fetch YouTube video metadata and transcripts. Provide a YouTube URL or video ID.",
)

# YouTube API client (lazy initialization)
_youtube_client = None


def get_youtube_client():
    """Get or create YouTube API client."""
    global _youtube_client
    if _youtube_client is None:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        _youtube_client = build("youtube", "v3", developerKey=api_key)
    return _youtube_client


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    # Common YouTube URL patterns
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",  # Direct video ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


@mcp.tool()
def get_video_metadata(youtube_url: str) -> dict:
    """
    Fetch metadata for a YouTube video.

    Args:
        youtube_url: YouTube video URL or video ID (e.g., 'https://youtube.com/watch?v=xxx' or 'xxx')

    Returns:
        Dictionary containing video metadata: title, description, channel, views, likes, duration, etc.
    """
    try:
        video_id = extract_video_id(youtube_url)
        youtube = get_youtube_client()

        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id,
        ).execute()

        if not response.get("items"):
            return {"error": f"Video not found: {video_id}"}

        video = response["items"][0]
        snippet = video["snippet"]
        stats = video.get("statistics", {})
        content = video.get("contentDetails", {})

        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "duration": content.get("duration"),
            "view_count": stats.get("viewCount"),
            "like_count": stats.get("likeCount"),
            "comment_count": stats.get("commentCount"),
            "tags": snippet.get("tags", []),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        }

    except ValueError as e:
        return {"error": str(e)}
    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        if e.resp.status == 403:
            return {"error": "API quota exceeded or invalid API key"}
        return {"error": f"YouTube API error: {e.resp.status}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_video_transcript(
    youtube_url: str,
    language: Optional[str] = None,
) -> dict:
    """
    Fetch transcript/captions for a YouTube video.

    Args:
        youtube_url: YouTube video URL or video ID
        language: Preferred language code (e.g., 'en', 'ko'). If not specified, defaults to English.

    Returns:
        Dictionary containing transcript text and metadata.
    """
    try:
        video_id = extract_video_id(youtube_url)
        api = YouTubeTranscriptApi()

        # Determine languages to try
        languages = [language] if language else ["en"]

        # Fetch transcript
        transcript = api.fetch(video_id, languages=languages)

        # Format transcript
        full_text = " ".join([snippet.text for snippet in transcript.snippets])
        segments = [
            {
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration,
            }
            for snippet in transcript.snippets
        ]

        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "full_text": full_text,
            "segments": segments,
            "segment_count": len(segments),
        }

    except ValueError as e:
        return {"error": str(e)}
    except TranscriptsDisabled:
        return {"error": "Transcripts are disabled for this video"}
    except VideoUnavailable:
        return {"error": "Video is unavailable"}
    except NoTranscriptFound:
        return {"error": "No transcript found for this video"}
    except Exception as e:
        logger.error(f"Transcript error: {e}")
        return {"error": f"Failed to fetch transcript: {str(e)}"}


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
