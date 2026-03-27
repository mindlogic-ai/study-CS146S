# Google Calendar MCP Server

A Model Context Protocol server that provides read-only access to Google Calendar via Claude Desktop.

## Prerequisites

- Python 3.10+
- Google Cloud project with Calendar API enabled
- OAuth 2.0 credentials (Desktop App type)

## Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and click "Enable"
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Configure OAuth consent screen if prompted (External, add your email as test user)
   - Choose **Desktop app** as application type
   - Download the JSON file

## Installation

```bash
# Install dependencies (if using conda)
conda activate cs146s
pip install mcp google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Set credentials path
export GOOGLE_CLIENT_SECRETS_PATH=/path/to/credentials.json
```

## First-time Authentication

Run the authentication module to complete OAuth flow:

```bash
cd week3
python -m server.auth
```

This opens a browser for OAuth consent. After granting access, tokens are saved to `~/.gcal-mcp/token.json`.

## Running the Server

```bash
cd week3
python -m server.main
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/week3",
      "env": {
        "GOOGLE_CLIENT_SECRETS_PATH": "/path/to/credentials.json"
      }
    }
  }
}
```

## Available Tools

### get_upcoming_events

Get upcoming calendar events starting from now.

**Parameters:**
- `calendar_id` (optional): Calendar ID to query. Default: "primary"
- `days_ahead` (optional): Number of days to look ahead (1-30). Default: 7
- `max_results` (optional): Maximum events to return (1-100). Default: 20

**Example:**
```
"What meetings do I have this week?"
"Show me my calendar for the next 3 days"
```

### search_events

Search for calendar events matching a query string.

**Parameters:**
- `query` (required): Search term to match against event title and description
- `calendar_id` (optional): Calendar ID to search. Default: "primary"
- `start_date` (optional): Start of search range (YYYY-MM-DD). Default: today
- `end_date` (optional): End of search range (YYYY-MM-DD). Default: 30 days from start
- `max_results` (optional): Maximum events to return (1-100). Default: 20

**Example:**
```
"Find all meetings about project review"
"Search for events with 'standup' in the title"
```

### get_event_details

Get detailed information about a specific calendar event.

**Parameters:**
- `event_id` (required): Event ID from get_upcoming_events or search_events results
- `calendar_id` (optional): Calendar ID containing the event. Default: "primary"

**Example:**
```
"Get details for event [event_id]"
"Who is attending the meeting [event_id]?"
```

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m server.main
```

## Troubleshooting

- **Token refresh errors**: Delete `~/.gcal-mcp/token.json` and re-authenticate
- **Rate limiting**: The server implements automatic retry with exponential backoff
- **Calendar not found**: Use "primary" for your main calendar

## Project Structure

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP server entrypoint
│   ├── auth.py              # OAuth2 authentication
│   ├── calendar_service.py  # Google Calendar API wrapper
│   └── config.py            # Configuration constants
└── README.md
```
