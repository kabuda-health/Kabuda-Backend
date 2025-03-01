from typing import Protocol

from authlib.integrations.starlette_client import (  # pyright: ignore[reportMissingImports]
    OAuth,
)
from fastapi import Request
from fastapi.datastructures import URL
from fastapi.responses import RedirectResponse

from app.settings import settings

GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"


class OAuthClient(Protocol):
    async def authorize_redirect(
        self, request: Request, redirect_uri: URL, access_type: str, state: str
    ) -> RedirectResponse: ...

    async def authorize_access_token(self, request: Request) -> dict: ...


class MockOAuthClient:
    def __init__(self, randomize: bool = False) -> None:
        self.randomize = randomize

    async def authorize_redirect(
        self, request: Request, redirect_uri: URL, access_type: str, state: str
    ) -> RedirectResponse:
        return RedirectResponse(
            url=redirect_uri.include_query_params(state=state), status_code=302
        )

    async def authorize_access_token(self, request: Request) -> dict:
        request_id = request.headers.get("X-Request-ID")
        name = "foo"
        if self.randomize:
            name = f"{name}-{request_id}"
        email = f"{name}@bar.com"
        return {
            "userinfo": {
                "name": name,
                "email": email,
            }
        }


class GoogleOAuthClient:
    def __init__(self) -> None:
        oauth_client = OAuth()
        oauth_client.register(
            name="google",
            client_id=settings.google_auth_client_id,
            client_secret=settings.google_auth_client_secret,
            server_metadata_url=GOOGLE_CONF_URL,
            client_kwargs={"scope": "openid email profile"},
        )
        self.oauth_client = oauth_client

    async def authorize_redirect(
        self, request: Request, redirect_uri: URL, access_type: str, state: str
    ) -> RedirectResponse:
        return await self.oauth_client.google.authorize_redirect(
            request, redirect_uri, access_type=access_type, state=state
        )

    async def authorize_access_token(self, request: Request) -> dict:
        return await self.oauth_client.google.authorize_access_token(request)
