from fastapi.testclient import TestClient

from app.models import Token


def test_it_works():
    assert True


def login(client: TestClient) -> Token:
    login_resp = client.get(
        "/api/auth/login/google",
        params={"redirect_uri": "/", "state": "test"},
    )
    url = login_resp.url
    code = url.params.get("code")
    assert code, "Code not found"
    token_resp = client.post(
        "/api/auth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
        },
    ).json()
    token = Token.model_validate(token_resp)
    return token


def test_oauth_flow(test_client: TestClient):
    login(test_client)


def test_refresh_tokens(test_client: TestClient):
    token = login(test_client)
    refresh_resp = test_client.post(
        "/api/auth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        },
    ).json()
    new_token = Token.model_validate(refresh_resp)
    assert new_token.access_token != token.access_token
    assert new_token.refresh_token != token.refresh_token
