import arrow
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from app.auth import AuthDep, RefreshDep, create_jwt, get_user_id, oauth


def access_token_expiry():
    return arrow.utcnow().shift(minutes=15)


def refresh_token_expiry():
    return arrow.utcnow().shift(days=7)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/login/google")
async def login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request, redirect_uri, access_type="offline"
    )


@router.get("/login/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]
    user_email = user_info["email"]
    user_id = get_user_id(user_email)
    user_name = user_info["name"]
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
    whoami_url = request.url_for("whoami")
    response = RedirectResponse(whoami_url)
    response.set_cookie("access_token", access_token)
    response.set_cookie("refresh_token", refresh_token)
    return response


@router.get("/whoami")
def whoami(jwt: AuthDep):
    return {"user_id": jwt["sub"], "name": jwt["name"], "email": jwt["email"]}


@router.get("/check-token")
def check_token(jwt: AuthDep):
    return jwt


@router.get("/refresh-token")
def refresh_token(jwt: RefreshDep, response: Response):
    user_id = jwt["sub"]
    user_name = jwt["name"]
    user_email = jwt["email"]
    access_token = create_jwt(
        user_id=user_id,
        name=user_name,
        email=user_email,
        exp=access_token_expiry(),
    )
    refresh_token = create_jwt(
        user_id=user_id,
        name=user_name,
        email=user_email,
        exp=refresh_token_expiry(),
    )
    response.set_cookie("access_token", access_token)
    response.set_cookie("refresh_token", refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}
