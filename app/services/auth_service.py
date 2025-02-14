import hashlib
import secrets
from typing import Optional

import arrow
import jwt
from authlib.integrations.starlette_client import OAuth
from loguru import logger

from app.models import Token
from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepo
from app.settings import settings

JWT_ALGORITHM = "HS256"
GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"


def access_token_expiry():
    return arrow.utcnow().shift(minutes=15)


def refresh_token_expiry():
    return arrow.utcnow().shift(days=7)


class InvalidGrantError(ValueError):
    pass


class InvalidTokenError(ValueError):
    pass


class AuthService:
    def __init__(self, user_repo: UserRepo) -> None:
        oauth_client = OAuth()
        oauth_client.register(
            name="google",
            client_id=settings.google_auth_client_id,
            client_secret=settings.google_auth_client_secret,
            server_metadata_url=GOOGLE_CONF_URL,
            client_kwargs={"scope": "openid email profile"},
        )
        self.oauth_client = oauth_client
        self.state_token_to_redirect_uri_map: dict[str, str] = {}
        self.access_code_to_user_data_map: dict[str, UserCreate] = {}
        self.user_repo = user_repo

    @staticmethod
    def create_jwt(user_id: str, name: str, email: str, exp: arrow.Arrow) -> str:
        payload = {"sub": user_id, "name": name, "email": email, "exp": exp.timestamp()}
        return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(token: str) -> dict:
        return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_access_token(self, token: str) -> dict:
        return self.verify_jwt(token)

    def verify_refresh_token(self, token: str) -> dict:
        data = self.verify_jwt(token)
        # TODO: Check against the database
        return data

    def cache_redirect_uri(self, key: Optional[str], redirect_uri: str) -> str:
        if key is None:
            key = secrets.token_urlsafe()
        self.state_token_to_redirect_uri_map[key] = redirect_uri
        return key

    def fetch_redirect_uri(self, key: str) -> str:
        return self.state_token_to_redirect_uri_map.pop(key)

    def cache_user_data(self, token: dict) -> str:
        access_code = secrets.token_urlsafe()
        user_info = token["userinfo"]
        user_data = UserCreate(name=user_info["name"], email=user_info["email"])
        self.access_code_to_user_data_map[access_code] = user_data
        return access_code

    def fetch_user_data(self, access_code: str) -> UserCreate:
        return self.access_code_to_user_data_map.pop(access_code)

    async def exchange_tokens(
        self, grant_type: str, code: Optional[str], refresh_token: Optional[str]
    ) -> Token:
        logger.info(f"{grant_type=}, {code=}, {refresh_token=}")
        async with self.user_repo.transaction():
            match grant_type:
                case "authorization_code" if code:
                    user_create = self.fetch_user_data(code)
                    user = await self.user_repo.get_user_by_email(user_create.email)
                    if user is None:
                        logger.info(f"Creating user: {user_create}")
                        user = await self.user_repo.create_user(user_create)
                case "refresh_token" if refresh_token:
                    try:
                        jwt = self.verify_refresh_token(refresh_token)
                        user = User(id=jwt["sub"], name=jwt["name"], email=jwt["email"])
                        session = await self.user_repo.get_session(
                            int(jwt["sub"]), self.hash_token(refresh_token)
                        )
                        if session is None:
                            raise ValueError("Invalid session")
                        if session.invalidated_at is not None:
                            logger.error(
                                "Detected reuse of invalidated refresh token! Invalidating all sessions"
                            )
                            await self.user_repo.invalidate_active_sessions(user.id)
                            # Manually commit here because on exception, the transaction context manager will rollback
                            await self.user_repo.commit()
                            raise ValueError(
                                "Reuse of refresh token detected, you may be compromised"
                            )
                    except Exception as e:
                        logger.error(f"Error validating refresh token: {e}")
                        raise InvalidTokenError(f"Invalid refresh token: {e}")
                case _:
                    raise InvalidGrantError(f"Invalid grant type: {grant_type}")
            access_token = self.create_jwt(
                user_id=str(user.id),
                name=user.name,
                email=user.email,
                exp=access_token_expiry(),
            )
            refresh_token = self.create_jwt(
                user_id=str(user.id),
                name=user.name,
                email=user.email,
                exp=refresh_token_expiry(),
            )
            await self.user_repo.invalidate_active_sessions(user.id)
            await self.user_repo.create_session(user.id, self.hash_token(refresh_token))
            return Token(access_token=access_token, refresh_token=refresh_token)
