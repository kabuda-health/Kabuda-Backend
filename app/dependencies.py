from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import AnyUrl
from sqlalchemy.ext.asyncio import create_async_engine

from app.models.user import User
from app.repositories.user_repository import PgUserRepo
from app.services.auth_service import AuthService
from app.settings import settings

oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/auth/login/google",
    tokenUrl="/api/auth/token",
    refreshUrl="/api/auth/token",
)

OAuthDep = Annotated[str, Depends(oauth2)]

pg_engine = create_async_engine(
    str(
        AnyUrl.build(
            scheme="postgresql+asyncpg",
            username=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            path=settings.db_name,
        )
    ),
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)

auth_service = AuthService(PgUserRepo(pg_engine))


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
