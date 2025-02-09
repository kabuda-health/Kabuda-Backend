from typing import Annotated

import arrow
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Cookie, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.settings import settings

JWT_ALGORITHM = "HS256"
GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/users/login/google",
    tokenUrl="/api/users/token",
    refreshUrl="/api/users/token",
)

OAuthDep = Annotated[str, Depends(oauth2_scheme)]


def create_jwt(user_id: str, name: str, email: str, exp: arrow.Arrow) -> str:
    payload = {"sub": user_id, "name": name, "email": email, "exp": exp.timestamp()}
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def get_user_id(username: str) -> int:
    # TODO: Implement this function
    return 1


def verify_access_token(access_token: OAuthDep) -> dict:
    try:
        return jwt.decode(access_token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


AuthDep = Annotated[dict, Depends(verify_access_token)]


def verify_refresh_token(refresh_token: str) -> dict:
    try:
        data = jwt.decode(
            refresh_token, settings.secret_key, algorithms=[JWT_ALGORITHM]
        )
        # TODO: Check against the database
        return data
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


RefreshDep = Annotated[dict, Depends(verify_refresh_token)]

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_auth_client_id,
    client_secret=settings.google_auth_client_secret,
    server_metadata_url=GOOGLE_CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)
