from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import AnyUrl
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.clients.oauth import GoogleOAuthClient
from app.models.user import User, UserCreate
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

auth_service = AuthService(PgUserRepo(pg_engine), GoogleOAuthClient())


def get_auth_service() -> AuthService:
    return auth_service


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_user(
    auth_service: AuthServiceDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )

    try:
        # Try iOS authentication first
        claims = await auth_service.oauth_client.verify_id_token(token)
        if not claims.get("email"):
            raise HTTPException(
                status_code=401, detail="Invalid ID token: missing email claim"
            )

        async with auth_service.user_repo.transaction() as tx:
            user = await tx.get_user_by_email(claims["email"])
            if user is None:
                user_create = UserCreate(name=claims["name"], email=claims["email"])
                user = await tx.create_user(user_create)
                return User.from_user_create(user_create, user.id)
            return User.from_user_create(
                UserCreate(name=user.name, email=user.email), user.id
            )
    except HTTPException:
        raise
    except Exception as e:
        # If iOS authentication fails, try web authentication
        try:
            payload = auth_service.verify_access_token(token)
            return User.from_jwt_payload(payload)
        except Exception as e2:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {str(e)} (iOS) or {str(e2)} (web)",
            )


UserDep = Annotated[User, Depends(get_user)]

async_session_maker = async_sessionmaker(
    pg_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
