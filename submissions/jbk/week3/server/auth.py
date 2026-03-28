"""OAuth 2.1 인가 서버 Provider — API key 검증 후 인가 코드 발급."""

import logging
import secrets
import time

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

logger = logging.getLogger(__name__)


class SimpleOAuthProvider:
    """인메모리 OAuth 2.1 인가 서버. API key 검증 후 인가 코드를 발급합니다."""

    def __init__(self, api_key: str, server_url: str):
        self.api_key = api_key
        self.server_url = server_url
        self.clients: dict[str, OAuthClientInformationFull] = {}
        self.auth_codes: dict[str, AuthorizationCode] = {}
        self.access_tokens: dict[str, AccessToken] = {}
        self.refresh_tokens: dict[str, RefreshToken] = {}
        self.pending_requests: dict[
            str, tuple[OAuthClientInformationFull, AuthorizationParams]
        ] = {}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self.clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self.clients[client_info.client_id] = client_info
        logger.info(f"OAuth client registered: {client_info.client_id}")

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        request_id = secrets.token_urlsafe(16)
        self.pending_requests[request_id] = (client, params)
        logger.info(f"OAuth authorize: waiting for API key from client {client.client_id}")
        return f"{self.server_url}/auth/login?request_id={request_id}"

    async def handle_login(self, request: Request) -> HTMLResponse:
        """API key 입력 폼을 보여줍니다."""
        request_id = request.query_params.get("request_id", "")
        error = request.query_params.get("error", "")
        error_html = '<p style="color:red;">API key가 올바르지 않습니다.</p>' if error else ""
        return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MCP Movie Server - 인증</title>
<style>
  body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center;
         height: 100vh; margin: 0; background: #1a1a2e; color: #eee; }}
  .card {{ background: #16213e; padding: 2rem; border-radius: 12px; width: 320px; }}
  h2 {{ margin-top: 0; }}
  input {{ width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box;
           border: 1px solid #555; border-radius: 6px; background: #0f3460; color: #eee; }}
  button {{ width: 100%; padding: 10px; background: #e94560; color: white; border: none;
            border-radius: 6px; cursor: pointer; font-size: 16px; }}
  button:hover {{ background: #c73e54; }}
</style></head>
<body><div class="card">
  <h2>MCP Movie Server</h2>
  <p>API key를 입력하세요.</p>
  {error_html}
  <form method="POST" action="/auth/verify">
    <input type="hidden" name="request_id" value="{request_id}">
    <input type="password" name="api_key" placeholder="API Key" autofocus>
    <button type="submit">인증</button>
  </form>
</div></body></html>""")

    async def handle_verify(self, request: Request) -> RedirectResponse | HTMLResponse:
        """API key를 검증하고 인가 코드를 발급합니다."""
        form = await request.form()
        api_key = form.get("api_key", "")
        request_id = form.get("request_id", "")

        pending = self.pending_requests.get(str(request_id))
        if not pending:
            return HTMLResponse("<h1>만료된 요청입니다.</h1>", status_code=400)

        if api_key != self.api_key:
            return RedirectResponse(
                f"/auth/login?request_id={request_id}&error=1", status_code=303
            )

        self.pending_requests.pop(str(request_id), None)
        client, params = pending

        code = secrets.token_urlsafe(32)
        self.auth_codes[code] = AuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + 300,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        logger.info(f"OAuth authorize: approved for client {client.client_id}")
        redirect_url = construct_redirect_uri(
            str(params.redirect_uri), code=code, state=params.state
        )
        return RedirectResponse(redirect_url, status_code=303)

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        ac = self.auth_codes.get(authorization_code)
        if ac and ac.client_id == client.client_id and ac.expires_at > time.time():
            return ac
        return None

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        self.auth_codes.pop(authorization_code.code, None)
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        self.access_tokens[access] = AccessToken(
            token=access,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=int(time.time()) + 3600,
        )
        self.refresh_tokens[refresh] = RefreshToken(
            token=refresh,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
        )
        logger.info(f"OAuth token issued for client {client.client_id}")
        return OAuthToken(
            access_token=access,
            refresh_token=refresh,
            expires_in=3600,
            token_type="Bearer",
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        rt = self.refresh_tokens.get(refresh_token)
        if rt and rt.client_id == client.client_id:
            return rt
        return None

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        self.refresh_tokens.pop(refresh_token.token, None)
        access = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)
        self.access_tokens[access] = AccessToken(
            token=access,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=int(time.time()) + 3600,
        )
        self.refresh_tokens[new_refresh] = RefreshToken(
            token=new_refresh,
            client_id=client.client_id,
            scopes=scopes,
        )
        logger.info(f"OAuth token refreshed for client {client.client_id}")
        return OAuthToken(
            access_token=access,
            refresh_token=new_refresh,
            expires_in=3600,
            token_type="Bearer",
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        at = self.access_tokens.get(token)
        if at and (at.expires_at is None or at.expires_at > int(time.time())):
            return at
        return None

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self.access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshToken):
            self.refresh_tokens.pop(token.token, None)
        logger.info(f"OAuth token revoked for client {token.client_id}")
