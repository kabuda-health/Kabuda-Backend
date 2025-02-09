from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.services.auth_service import AuthService

oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/auth/login/google",
    tokenUrl="/api/auth/token",
    refreshUrl="/api/auth/token",
)

OAuthDep = Annotated[str, Depends(oauth2)]

auth_service = AuthService()


def get_auth_service() -> AuthService:
    return auth_service


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_oauth_client(auth_service: AuthServiceDep) -> OAuth:
    return auth_service.oauth_client


OAuthClientDep = Annotated[OAuth, Depends(get_oauth_client)]


def get_current_user(token: OAuthDep, auth_service: AuthServiceDep) -> dict:
    try:
        payload = auth_service.verify_access_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Verify access token failed: {e}")


UserDep = Annotated[dict, Depends(get_current_user)]
