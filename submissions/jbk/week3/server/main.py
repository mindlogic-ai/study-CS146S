"""
MCP Movie Server - TMDB API를 활용한 영화 정보 서버

STDIO(로컬), SSE(HTTP), Streamable HTTP transport를 지원하며,
Streamable HTTP 모드에서는 OAuth 2.1 인증을 적용합니다.
"""

import argparse
import logging
import os

from dotenv import load_dotenv

load_dotenv()
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
from mcp.server.fastmcp import FastMCP

from .auth import SimpleOAuthProvider
from .tools import register_tools


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_mcp_server(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> FastMCP:
    """transport 모드에 따라 적절한 FastMCP 인스턴스를 생성합니다."""

    if transport == "streamable-http":
        server_url = os.getenv("MCP_SERVER_URL", f"http://{host}:{port}")
        mcp_api_key = os.getenv("MCP_API_KEY", "")
        if not mcp_api_key:
            logger.warning("MCP_API_KEY not set — 인증 시 어떤 키든 거부됩니다!")

        provider = SimpleOAuthProvider(api_key=mcp_api_key, server_url=server_url)
        mcp = FastMCP(
            "movie-server",
            host=host,
            port=port,
            auth_server_provider=provider,
            auth=AuthSettings(
                issuer_url=server_url,
                resource_server_url=server_url,
                client_registration_options=ClientRegistrationOptions(
                    enabled=True,
                    valid_scopes=["mcp:tools/call"],
                    default_scopes=["mcp:tools/call"],
                ),
                required_scopes=["mcp:tools/call"],
            ),
        )
        register_tools(mcp)
        mcp._oauth_provider = provider
        logger.info(f"Created Streamable HTTP server with OAuth on {server_url}")
        return mcp
    elif transport == "sse":
        mcp = FastMCP("movie-server", host=host, port=port)
    else:
        mcp = FastMCP("movie-server")
        logger.info("Created STDIO server")

    register_tools(mcp)
    return mcp


def main():
    """서버 실행"""
    import uvicorn

    parser = argparse.ArgumentParser(description="MCP Movie Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport 모드: stdio (로컬), sse (HTTP), streamable-http (OAuth 인증)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="서버 호스트 (기본: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="서버 포트 (기본: 8000)")
    args = parser.parse_args()

    logger.info(f"Movie MCP Server starting... (transport={args.transport})")

    mcp = create_mcp_server(
        transport=args.transport,
        host=args.host,
        port=args.port,
    )

    if args.transport == "streamable-http":
        provider: SimpleOAuthProvider = mcp._oauth_provider
        mcp_app = mcp.streamable_http_app()
        mcp_app.add_route("/auth/login", provider.handle_login, methods=["GET"])
        mcp_app.add_route("/auth/verify", provider.handle_verify, methods=["POST"])
        config = uvicorn.Config(mcp_app, host=args.host, port=args.port, log_level="info")
        server = uvicorn.Server(config)
        import anyio

        anyio.run(server.serve)
    else:
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
