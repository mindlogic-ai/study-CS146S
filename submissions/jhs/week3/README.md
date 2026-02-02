# Week 3 MCP Servers

Two MCP servers built with FastMCP for fetching external data.

## Servers

| Server | Directory | API | Auth Required |
|--------|-----------|-----|---------------|
| YouTube | `youtube-server/` | YouTube Data API | Yes (API key) |
| ClawNews | `clawnews-server/` | ClawNews.io | No |

## Quick Setup

Copy the template and update paths:

```bash
cp .mcp.template.json ~/.mcp.json  # or your project's .mcp.json
# Edit the paths and add your YOUTUBE_API_KEY
```

---

# YouTube MCP Server

An MCP server that fetches YouTube video metadata and transcripts.

## Features

- **get_video_metadata**: Fetches title, description, channel, views, likes, duration, tags, and thumbnail
- **get_video_transcript**: Fetches video captions/transcripts with timestamps

## Prerequisites

- Python 3.10+
- YouTube Data API key ([Get one here](https://console.cloud.google.com/apis/credentials))
- uv (recommended) or pip

## Setup

### 1. Install dependencies

```bash
cd submissions/jhs/week3/youtube-server
uv sync
```

### 2. Set environment variable

```bash
export YOUTUBE_API_KEY=your_api_key_here
```

### 3. Test the server

```bash
uv run fastmcp dev main.py
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "youtube": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/submissions/jhs/week3/youtube-server", "fastmcp", "run", "main.py"],
      "env": {
        "YOUTUBE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Tool Reference

### get_video_metadata

Fetches metadata for a YouTube video.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `youtube_url` | string | Yes | YouTube URL or video ID |

**Example Output:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "Rick Astley",
  "view_count": "1500000000",
  "like_count": "15000000"
}
```

### get_video_transcript

Fetches transcript/captions for a YouTube video.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `youtube_url` | string | Yes | YouTube URL or video ID |
| `language` | string | No | Preferred language code (e.g., 'en', 'ko') |

**Example Output:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en (auto-generated)",
  "full_text": "We're no strangers to love...",
  "segment_count": 42
}
```

---

# ClawNews MCP Server

An MCP server that fetches AI agent news from [ClawNews.io](https://clawnews.io) - "Hacker News for AI agents."

## Features

- **get_top_stories**: Fetches top trending stories from ClawNews
- **get_digest**: Fetches daily curated digest of AI agent news
- **get_story**: Fetches a specific story with comments

## Prerequisites

- Python 3.10+
- uv (recommended) or pip
- No API key required!

## Setup

### 1. Install dependencies

```bash
cd submissions/jhs/week3/clawnews-server
uv sync
```

### 2. Test the server

```bash
uv run fastmcp dev main.py
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "clawnews": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/submissions/jhs/week3/clawnews-server", "fastmcp", "run", "main.py"]
    }
  }
}
```

## Tool Reference

### get_top_stories

Fetches top stories from ClawNews.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Number of stories (default 10, max 30) |

**Example Input:**
```
limit: 5
```

**Example Output:**
```json
{
  "stories": [
    {
      "id": 123,
      "title": "Building Autonomous Agents with Memory",
      "url": "https://example.com/article",
      "score": 142,
      "by": "agent_smith",
      "comment_count": 23
    }
  ],
  "count": 5,
  "source": "clawnews.io"
}
```

### get_digest

Fetches the daily digest from ClawNews.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | No | Date in YYYY-MM-DD format (default: today) |

**Example Input:**
```
date: "2025-01-15"
```

**Example Output:**
```json
{
  "date": "2025-01-15",
  "title": "Daily Digest",
  "summary": "Top stories in AI agents today...",
  "stories": [...],
  "story_count": 12,
  "source": "clawnews.io"
}
```

### get_story

Fetches a specific story with its comments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `story_id` | int | Yes | The numeric ID of the story |

**Example Input:**
```
story_id: 123
```

**Example Output:**
```json
{
  "id": 123,
  "title": "Building Autonomous Agents with Memory",
  "url": "https://example.com/article",
  "text": "Full article text if self-post...",
  "by": "agent_smith",
  "score": 142,
  "comment_count": 23,
  "comments": [
    {"id": 456, "by": "neo", "text": "Great article!"}
  ],
  "source": "clawnews.io"
}
```

---

## Error Handling

Both servers implement graceful error handling:

- HTTP errors return `{"error": "HTTP error: <status_code>"}`
- Rate limits return `{"error": "Rate limit exceeded. Please try again later."}`
- Connection errors return `{"error": "Failed to connect to <service>: <details>"}`
- Not found errors return `{"error": "<resource> not found: <id>"}`

## Example Usage Flow

### YouTube
1. "Get the metadata for https://www.youtube.com/watch?v=dQw4w9WgXcQ"
2. "Now get the transcript for that video"
3. "Summarize what this video is about"

### ClawNews
1. "What are the top 5 stories on ClawNews right now?"
2. "Get today's digest from ClawNews"
3. "Tell me more about story #123"
