"""FastAPI application factory."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="docpybara", version="0.1.0")

    root_dir = os.environ.get("DOCPYBARA_ROOT_DIR", ".")
    app.state.root_dir = Path(root_dir).resolve()

    # Register routers
    from docpybara.routers.ai import router as ai_router
    from docpybara.routers.files import router as files_router
    from docpybara.routers.search import router as search_router

    app.include_router(files_router, prefix="/api")
    app.include_router(search_router, prefix="/api")
    app.include_router(ai_router, prefix="/api")

    # Serve static frontend files
    static_dir = Path(__file__).parent / "static"
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
