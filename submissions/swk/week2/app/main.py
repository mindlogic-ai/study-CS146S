"""
FastAPI application entry point for Action Item Extractor.

This module configures the FastAPI app, initializes the database on startup,
and mounts routers and static files.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import action_items, notes


# -----------------------------------------------------------------------------
# App Lifecycle (Refactored: use lifespan instead of module-level init)
# -----------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Initializes the database on startup and performs cleanup on shutdown.
    """
    init_db()
    yield


# -----------------------------------------------------------------------------
# FastAPI App Configuration (Refactored: added description and version)
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Action Item Extractor",
    description="Extract action items from free-form notes using rules or LLM",
    version="1.0.0",
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["frontend"])
def index() -> str:
    """Serve the frontend HTML page."""
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


# Include routers
app.include_router(notes.router)
app.include_router(action_items.router)


# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------

static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")