"""FastAPI application factory."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    root_dir = Path(os.environ.get("DOCPYBARA_ROOT_DIR", ".")).resolve()

    # Set up MCP server
    from docpybara.mcp_server import mcp, set_root_dir

    set_root_dir(root_dir)
    mcp_app = mcp.http_app(path="/", transport="streamable-http")

    # Use MCP app's lifespan so its session manager is properly initialized
    app = FastAPI(title="docpybara", version="0.1.0", lifespan=mcp_app.lifespan)
    app.state.root_dir = root_dir

    # Register routers
    from docpybara.routers.ai import router as ai_router
    from docpybara.routers.files import router as files_router
    from docpybara.routers.search import router as search_router

    app.include_router(files_router, prefix="/api")
    app.include_router(search_router, prefix="/api")
    app.include_router(ai_router, prefix="/api")

    # Mount MCP server at /mcp
    app.mount("/mcp", mcp_app)

    # Serve static frontend files (must be last — catches all routes)
    static_dir = Path(__file__).parent / "static"
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
