# Hacker News MCP Server

A Model Context Protocol (MCP) server that wraps the Hacker News Firebase API, enabling AI models and MCP clients to fetch and search stories, retrieve user profiles, and access comments. Supports both STDIO (local) and HTTP (remote) transports with optional API key authentication.

## Features

- **4 MCP Tools**: `get_top_stories`, `get_story_details`, `get_user_profile`, `search_stories`
- **Multiple Transports**: STDIO for local Claude Desktop integration, HTTP for remote deployment
- **API Key Authentication**: Optional bearer token validation for HTTP transport
- **Async HTTP Client**: Uses httpx with connection pooling and semaphore-based concurrency control
- **Robust Error Handling**: Retry logic with exponential backoff, validation, and graceful degradation
- **Type Safety**: Full Pydantic v2 validation for request/response models

## Prerequisites

- Python 3.10+ (3.12 recommended)
- Poetry (dependency management)
- Conda (optional, recommended for environment isolation)

## Setup Instructions

### 1. Clone and Navigate

```bash
# From the root study-CS146S directory
cd submissions/pky/week3
```

### 2. Create Python Environment (Optional but Recommended)

Using Conda:
```bash
conda create -n cs146s-week3 python=3.12 -y
conda activate cs146s-week3
```

Or use your system Python 3.10+ directly.

### 3. Install Dependencies

```bash
poetry install
```

This installs all dependencies declared in `pyproject.toml` including the MCP SDK, httpx, Pydantic, and test tooling.

### 4. Configure Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env` to set your API key (for HTTP mode):
```bash
# .env
HN_MCP_API_KEY=your-secure-random-string-here
```

To generate a secure random API key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Note**: For STDIO mode (local development), you can leave the API key empty or unset.

## Running the Server

### STDIO Transport (Local, Claude Desktop Integration)

Start the server in STDIO mode (no API key required, no listening port):

```bash
poetry run python -m server.main
```

The server reads stdin and writes to stdout, conforming to the MCP STDIO protocol. Suitable for local testing and Claude Desktop integration.

### HTTP Transport (Remote, Network Accessible)

Start the server in HTTP mode with API key authentication:

```bash
poetry run python -m server.main --http
```

The server listens on `http://localhost:8000/mcp` with `/call`, `/call_with_result`, and `/initialize` endpoints. Requires a valid `HN_MCP_API_KEY` environment variable for client requests.

## Claude Desktop Integration

To use this MCP server with Claude Desktop (local STDIO mode):

1. Open Claude Desktop settings
2. Locate the MCP configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Add the Hacker News MCP server to your configuration:

```json
{
  "mcpServers": {
    "hackernews": {
      "command": "poetry",
      "args": ["run", "python", "-m", "server.main"],
      "cwd": "/absolute/path/to/submissions/pky/week3"
    }
  }
}
```

Replace `/absolute/path/to/submissions/pky/week3` with the actual full path. You can verify the path with:

```bash
pwd
```

4. Restart Claude Desktop
5. The Hacker News tools should now appear in the Tools panel

## Tool Reference

All tools return JSON responses. Errors include an `"error"` key with details.

### get_top_stories

Fetch top, newest, best, ask, show, or job stories from Hacker News.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | `"top"` | Story category: `top`, `new`, `best`, `ask`, `show`, `job` |
| `limit` | integer | `10` | Number of stories to return (1-30) |

**Example Invocation:**
```bash
poetry run python -c "
import asyncio
from server.hn_client import HNClient
from server.models import StoryItem

async def test():
    client = HNClient()
    await client.start()
    stories = await client.fetch_stories(category='top', limit=5)
    for s in stories:
        print(f'{s.id}: {s.title} ({s.score} points)')
    await client.close()

asyncio.run(test())
"
```

**Example Response:**
```json
[
  {
    "id": 39473289,
    "title": "The Unreasonable Effectiveness of C",
    "url": "https://example.com/article",
    "score": 1205,
    "author": "dang",
    "time": "2025-01-30T15:45:00+00:00",
    "comment_count": 89
  },
  {
    "id": 39472654,
    "title": "Show HN: New Project Framework",
    "url": "https://github.com/example/framework",
    "score": 892,
    "author": "pg",
    "time": "2025-01-30T14:22:00+00:00",
    "comment_count": 145
  }
]
```

### get_story_details

Fetch detailed information about a single story, optionally including top-level comments.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `story_id` | integer | required | The Hacker News numeric item ID |
| `include_comments` | boolean | `false` | Whether to fetch top-level comments |
| `comment_limit` | integer | `5` | Maximum comments to include (1-20), ignored if `include_comments=false` |

**Example Invocation:**
```bash
poetry run python -c "
import asyncio
from server.hn_client import HNClient

async def test():
    client = HNClient()
    await client.start()
    story = await client.fetch_story_details(39473289)
    if story:
        print(f'Title: {story.title}')
        print(f'Score: {story.score}')
        print(f'Comments: {story.comment_count}')
    await client.close()

asyncio.run(test())
"
```

**Example Response (with comments):**
```json
{
  "id": 39473289,
  "title": "The Unreasonable Effectiveness of C",
  "url": "https://example.com/article",
  "score": 1205,
  "author": "dang",
  "time": "2025-01-30T15:45:00+00:00",
  "comment_count": 89,
  "type": "story",
  "text": null,
  "comments": [
    {
      "id": 39473456,
      "text": "This is a fascinating discussion about language design...",
      "author": "user123",
      "time": "2025-01-30T16:00:00+00:00"
    },
    {
      "id": 39473489,
      "text": "The author makes some great points about backward compatibility...",
      "author": "user456",
      "time": "2025-01-30T16:15:00+00:00"
    }
  ]
}
```

### get_user_profile

Fetch a user's profile information including karma, submission count, and account age.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | The Hacker News username (case-sensitive) |

**Example Invocation:**
```bash
poetry run python -c "
import asyncio
from server.hn_client import HNClient

async def test():
    client = HNClient()
    await client.start()
    user = await client.fetch_user('dang')
    if user:
        print(f'Karma: {user.karma}')
        print(f'Submissions: {user.submission_count}')
    await client.close()

asyncio.run(test())
"
```

**Example Response:**
```json
{
  "id": "dang",
  "karma": 567890,
  "created": "2007-10-19T02:57:00+00:00",
  "about": "HN moderator",
  "submission_count": 5234
}
```

### search_stories

Search recent stories by keyword in title (client-side filtering). Searches the top 100 stories in a category and filters by case-insensitive title match.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Search term to match against story titles (case-insensitive) |
| `category` | string | `"top"` | Story list to search: `top`, `new`, `best` |
| `limit` | integer | `10` | Maximum results to return (1-20) |

**Example Invocation:**
```bash
poetry run python -c "
import asyncio
from server.hn_client import HNClient

async def test():
    client = HNClient()
    await client.start()
    results = await client.search_stories(keyword='rust', category='top', limit=5)
    for story in results:
        print(f'{story.id}: {story.title}')
    await client.close()

asyncio.run(test())
"
```

**Example Response:**
```json
{
  "keyword": "rust",
  "count": 3,
  "stories": [
    {
      "id": 39472654,
      "title": "Rust 1.85 Released: Enhanced Async Performance",
      "url": "https://example.com/rust-1.85",
      "score": 1456,
      "author": "rustbot",
      "time": "2025-01-30T12:00:00+00:00",
      "comment_count": 234
    },
    {
      "id": 39471890,
      "title": "Show HN: Rust Web Framework for MCP Servers",
      "url": "https://github.com/example/mcp-web",
      "score": 678,
      "author": "developer",
      "time": "2025-01-30T11:30:00+00:00",
      "comment_count": 45
    }
  ]
}
```

## Authentication

### STDIO Mode (Local)

No authentication required. STDIO servers communicate via stdin/stdout with trusted local clients.

### HTTP Mode (Remote)

API key authentication is enforced via bearer tokens in the `Authorization` header.

**Setting the API Key:**

```bash
# Generate a secure key
export HN_MCP_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Start the server
poetry run python -m server.main --http
```

**Making Authenticated Requests:**

```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_top_stories",
      "arguments": {"category": "top", "limit": 5}
    }
  }'
```

**Development Mode (No Auth):**

If `HN_MCP_API_KEY` is not set, the server allows all requests (development convenience). Always set this in production.

## Running Tests

Run the test suite with pytest:

```bash
poetry run pytest -v
```

This runs all tests in the `tests/` directory with verbose output. Tests use mocked HTTP responses via `respx` to avoid network calls.

### Test Coverage

- `conftest.py`: Shared fixtures for story/comment/user data and mocked client
- Additional test files can be added for `hn_client.py`, `auth.py`, etc.

## Code Quality

Format and lint your code to maintain consistency:

### Format with Black

```bash
poetry run black .
```

Configured for 100-character line length per project standards.

### Lint with Ruff

```bash
poetry run ruff check .
```

Checks enabled: E (errors), F (pyflakes), I (import sorting), UP (upgrades), B (bugbear).

### All Together

```bash
poetry run black . && poetry run ruff check .
```

## Architecture

The server is organized into focused modules:

```
server/
  main.py       - Server entrypoint, lifespan management, HTTP/STDIO mode selection
  config.py     - Pydantic Settings for environment variables and configuration
  auth.py       - API key authentication provider for HTTP transport
  tools.py      - MCP tool definitions (get_top_stories, get_story_details, etc.)
  hn_client.py  - Async HTTP client for Hacker News Firebase API
  models.py     - Pydantic data models (StoryItem, CommentItem, UserProfile)
  __init__.py   - Package marker

tests/
  conftest.py   - Shared pytest fixtures for testing
  __init__.py   - Package marker
```

### Key Design Patterns

**Async/Await Throughout**: All I/O operations are async using httpx and asyncio, allowing the server to handle concurrent requests efficiently.

**Semaphore Concurrency Control**: A configurable semaphore limits concurrent API requests to the HN service (default: 30 concurrent requests). This respects the API's rate limits and prevents resource exhaustion.

**Lifespan Management**: The FastMCP server's lifespan context creates the HNClient once on startup and closes it on shutdown, ensuring proper resource cleanup.

**Client-Side Search**: Since the Hacker News API has no built-in search endpoint, `search_stories` fetches recent stories and filters client-side. The search scans the top 100 stories in a category for efficiency.

**Retry Logic with Backoff**: Transient errors (timeouts, 5xx responses) trigger exponential backoff retry (2^attempt seconds). Client errors (4xx) fail immediately.

**Type Validation**: Pydantic models validate all API responses. Malformed or unexpected fields are logged but don't crash the server.

## Technical Decisions

### Why httpx?

httpx provides async HTTP support with built-in connection pooling, timeout handling, and a familiar requests-like API. It's ideal for MCP servers that may serve many concurrent clients.

### Why Semaphore for Concurrency?

The Hacker News API is a shared resource. A semaphore limits concurrent requests to prevent overwhelming the service and respects rate-limit conventions. It's simpler and more effective than per-client rate limiting.

### Why Client-Side Search?

The Hacker News Firebase API exposes only story lists (top/new/best/etc.), not a search endpoint. Implementing search client-side keeps the MCP server decoupled from third-party search services and provides fast, simple keyword matching in titles.

### Why Pydantic?

Pydantic v2 provides runtime type validation, computed fields (like `time_iso` for ISO timestamp conversion), and clear error messages. It ensures the server handles incomplete or malformed API responses gracefully.

### Why Separate Models for Each Item Type?

`StoryItem`, `CommentItem`, and `UserProfile` each have specific fields and behaviors. Separate models prevent confusion and allow independent evolution of each data type.

## Troubleshooting

### "HNClient not started" Error

The HNClient must be started before use. Ensure the server's lifespan context is running. This error indicates the context wasn't initialized properly.

```python
# Wrong: direct instantiation
client = HNClient()
await client.fetch_stories()  # RuntimeError!

# Correct: via server lifespan
# Server calls client.start() automatically
```

### "Invalid API key" in HTTP Mode

Verify the `Authorization` header uses the correct format:
```bash
Authorization: Bearer <your-api-key>
```

Check that `HN_MCP_API_KEY` environment variable matches the key in your request.

### Timeouts Fetching Large Comment Threads

Comment fetching is limited to 20 per request for performance. If a story has many comments, only the top 20 (by HN's ordering) are available. Adjust `comment_limit` in `get_story_details` to fetch fewer.

### "Connection refused" in HTTP Mode

Ensure the server is running:
```bash
poetry run python -m server.main --http
```

Check that port 8000 is available. To use a different port, modify `server_port` in `.env`:
```bash
SERVER_PORT=9000
```

Then start with `--http` flag (port is read from config).

### STDIO Server Won't Start

Ensure stdout/stderr are not being used by other code. STDIO servers reserve stdout for the protocol. All logging goes to stderr automatically.

## Dependencies

- **mcp** (>=1.0.0) - Model Context Protocol SDK
- **httpx** (>=0.27.0) - Async HTTP client
- **pydantic** (>=2.0.0) - Data validation and parsing
- **pydantic-settings** (>=2.0.0) - Settings management from environment
- **python-dotenv** (>=1.0.0) - .env file loading

**Dev Dependencies:**
- **pytest** (>=7.0.0) - Testing framework
- **pytest-asyncio** (>=0.23.0) - Async test support
- **respx** (>=0.21.0) - HTTP mocking for tests

## References

- Hacker News API Documentation: https://github.com/HackerNews/API
- Model Context Protocol: https://modelcontextprotocol.io
- MCP Authorization Specification: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- httpx Documentation: https://www.python-httpx.org/
- Pydantic Documentation: https://docs.pydantic.dev/latest/

## License

This project is part of the CS146S coursework at Stanford.
