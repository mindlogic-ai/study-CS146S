"""Google Calendar MCP Server - Simple implementation."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# MCP Server
mcp = FastMCP("google-calendar")

# Google Calendar API setup
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PATH = Path.home() / ".gcal-mcp" / "token.json"
CREDENTIALS_PATH = Path(os.getenv("GOOGLE_CLIENT_SECRETS_PATH", "credentials.json"))


def get_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


@mcp.tool()
def get_upcoming_events(days_ahead: int = 7, max_results: int = 10) -> list[dict]:
    """
    Get upcoming calendar events.

    Args:
        days_ahead: Number of days to look ahead (default: 7)
        max_results: Maximum events to return (default: 10)
    """
    service = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=end,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    return [
        {
            "id": e.get("id"),
            "summary": e.get("summary", "(No title)"),
            "start": e.get("start", {}).get("dateTime") or e.get("start", {}).get("date"),
            "end": e.get("end", {}).get("dateTime") or e.get("end", {}).get("date"),
            "location": e.get("location"),
        }
        for e in events
    ]


@mcp.tool()
def search_events(query: str, days_ahead: int = 30) -> list[dict]:
    """
    Search calendar events by keyword.
 
    Args:
        query: Search term to match
        days_ahead: Days to search ahead (default: 30)
    """
    service = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=end,
        q=query,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    return [
        {
            "id": e.get("id"),
            "summary": e.get("summary", "(No title)"),
            "start": e.get("start", {}).get("dateTime") or e.get("start", {}).get("date"),
            "end": e.get("end", {}).get("dateTime") or e.get("end", {}).get("date"),
            "location": e.get("location"),
        }
        for e in events
    ]


if __name__ == "__main__":
    mcp.run()
