import asyncio
import secrets
from typing import Callable

import pytest
from httpx import AsyncClient

from app.models import Token


def test_it_works() -> None:
    assert True


async def login(client: AsyncClient) -> Token:
    login_resp = await client.get(
        "/api/auth/login/google",
        params={"redirect_uri": "/", "state": secrets.token_urlsafe()},
    )
    url = login_resp.url
    code = url.params.get("code")
    assert code, "Code not found"
    token_resp = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
        },
    )
    token_json = token_resp.json()
    token = Token.model_validate(token_json)
    return token


@pytest.mark.asyncio
async def test_oauth_flow(test_client: AsyncClient) -> None:
    await login(test_client)


@pytest.mark.asyncio
async def test_refresh_tokens(test_client: AsyncClient) -> None:
    token = await login(test_client)
    refresh_resp = await test_client.post(
        "/api/auth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        },
    )
    refresh_token_json = refresh_resp.json()
    new_token = Token.model_validate(refresh_token_json)
    assert new_token.access_token != token.access_token
    assert new_token.refresh_token != token.refresh_token


@pytest.mark.asyncio
async def test_concurrent_logins(
    test_client_builder: Callable[..., AsyncClient],
) -> None:
    async with test_client_builder(randomize_user=True) as test_client:
        coros = [login(test_client) for _ in range(10)]
        await asyncio.gather(*coros)
