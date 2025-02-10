from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.models.user import User
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


def get_current_user(token: OAuthDep, auth_service: AuthServiceDep) -> User:
    try:
        payload = auth_service.verify_access_token(token)
        return User.from_jwt_payload(payload)
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Verify access token failed: {e}")


UserDep = Annotated[User, Depends(get_current_user)]
