import urllib.parse
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.dependencies import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/google")
async def login(
    request: Request,
    redirect_uri: str,
    state: Optional[str],
    auth_service: AuthServiceDep,
):
    state_token = auth_service.cache_redirect_uri(state, redirect_uri)
    google_callback_uri = request.url_for("google_callback")
    return await auth_service.oauth_client.google.authorize_redirect(
        request, google_callback_uri, access_type="offline", state=state_token
    )


@router.get("/login/google/callback")
async def google_callback(request: Request, state: str, auth_service: AuthServiceDep):
    user_data = await auth_service.oauth_client.google.authorize_access_token(request)
    access_code = auth_service.cache_user_data(user_data)
    redirect_uri = (
        auth_service.fetch_redirect_uri(state)
        + "?"
        + urllib.parse.urlencode({"code": access_code, "state": state})
    )
    return RedirectResponse(url=redirect_uri, status_code=302)


@router.post("/token")
async def token(
    auth_service: AuthServiceDep,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
):
    try:
        return auth_service.exchange_tokens(grant_type, code, refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
