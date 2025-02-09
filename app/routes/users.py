import secrets
import urllib.parse
from typing import Optional

import arrow
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger

from app.auth import AuthDep, create_jwt, get_user_id, oauth, verify_refresh_token


def access_token_expiry():
    return arrow.utcnow().shift(minutes=15)


def refresh_token_expiry():
    return arrow.utcnow().shift(days=7)


router = APIRouter(prefix="/users", tags=["users"])

STATE_TOKEN_TO_REDIRECT_URI_MAP: dict[str, str] = {}
ACCESS_CODE_TO_USER_DATA_MAP: dict[str, dict] = {}


@router.get("/login/google")
async def login(request: Request):
    state_token = request.query_params.get("state", secrets.token_urlsafe())
    redirect_uri = request.query_params["redirect_uri"]
    STATE_TOKEN_TO_REDIRECT_URI_MAP[state_token] = redirect_uri
    google_callback_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request, google_callback_uri, access_type="offline", state=state_token
    )


@router.get("/login/google/callback")
async def google_callback(request: Request):
    state_token = request.query_params["state"]
    access_code = secrets.token_urlsafe()
    token = await oauth.google.authorize_access_token(request)
    ACCESS_CODE_TO_USER_DATA_MAP[access_code] = token
    redirect_uri = (
        STATE_TOKEN_TO_REDIRECT_URI_MAP[state_token]
        + "?"
        + urllib.parse.urlencode({"code": access_code, "state": state_token})
    )
    return RedirectResponse(url=redirect_uri, status_code=302)


@router.get("/whoami")
def whoami(jwt: AuthDep):
    return {"user_id": jwt["sub"], "name": jwt["name"], "email": jwt["email"]}


@router.get("/check-token")
def check_token(jwt: AuthDep):
    return jwt


@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
):
    logger.info(f"{grant_type=}, {code=}, {refresh_token=}")
    match grant_type:
        case "authorization_code" if code:
            token = ACCESS_CODE_TO_USER_DATA_MAP[code]
            user_info = token["userinfo"]
            user_email = user_info["email"]
            user_id = get_user_id(user_email)
            user_name = user_info["name"]
        case "refresh_token" if refresh_token:
            jwt = verify_refresh_token(refresh_token)
            user_email = jwt["email"]
            user_id = jwt["sub"]
            user_name = jwt["name"]
        case _:
            raise HTTPException(status_code=400, detail="invalid_grant")
    access_token = create_jwt(
        user_id=str(user_id),
        name=user_name,
        email=user_email,
        exp=access_token_expiry(),
    )
    refresh_token = create_jwt(
        user_id=str(user_id),
        name=user_name,
        email=user_email,
        exp=refresh_token_expiry(),
    )
    return {"access_token": access_token, "refresh_token": refresh_token}
