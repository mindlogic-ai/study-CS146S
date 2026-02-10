"""TODO 3: Refactored app entry point with lifespan-based DB init and cleaner config."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import action_items, notes

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"


# --- App lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database on startup."""
    init_db()
    yield


app = FastAPI(title="Action Item Extractor", lifespan=lifespan)


# --- Routes ---
@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)

# --- Static files ---
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
