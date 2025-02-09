import secrets
from typing import Optional

import arrow
import jwt
from authlib.integrations.starlette_client import OAuth
from loguru import logger

from app.settings import settings

JWT_ALGORITHM = "HS256"
GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"


def access_token_expiry():
    return arrow.utcnow().shift(minutes=15)


def refresh_token_expiry():
    return arrow.utcnow().shift(days=7)


class AuthService:

    oauth_client = OAuth()
    oauth_client.register(
        name="google",
        client_id=settings.google_auth_client_id,
        client_secret=settings.google_auth_client_secret,
        server_metadata_url=GOOGLE_CONF_URL,
        client_kwargs={"scope": "openid email profile"},
    )
    state_token_to_redirect_uri_map: dict[str, str] = {}
    access_code_to_user_data_map: dict[str, dict] = {}

    @staticmethod
    def create_jwt(user_id: str, name: str, email: str, exp: arrow.Arrow) -> str:
        payload = {"sub": user_id, "name": name, "email": email, "exp": exp.timestamp()}
        return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(token: str) -> dict:
        return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])

    def verify_access_token(self, token: str) -> dict:
        return self.verify_jwt(token)

    def verify_refresh_token(self, token: str) -> dict:
        data = self.verify_jwt(token)
        # TODO: Check against the database
        return data

    def get_user_id(self, user_email: str) -> int:
        # TODO: Implement this function
        return 1

    def cache_redirect_uri(self, key: Optional[str], redirect_uri: str) -> str:
        if key is None:
            key = secrets.token_urlsafe()
        self.state_token_to_redirect_uri_map[key] = redirect_uri
        return key

    def fetch_redirect_uri(self, key: str) -> str:
        return self.state_token_to_redirect_uri_map.pop(key)

    def cache_user_data(self, user_data: dict) -> str:
        access_code = secrets.token_urlsafe()
        self.access_code_to_user_data_map[access_code] = user_data
        return access_code

    def fetch_user_data(self, access_code: str) -> dict:
        return self.access_code_to_user_data_map.pop(access_code)

    def exchange_tokens(
        self, grant_type: str, code: Optional[str], refresh_token: Optional[str]
    ) -> dict:
        logger.info(f"{grant_type=}, {code=}, {refresh_token=}")
        match grant_type:
            case "authorization_code" if code:
                token = self.fetch_user_data(code)
                user_info = token["userinfo"]
                user_email = user_info["email"]
                user_id = self.get_user_id(user_email)
                user_name = user_info["name"]
            case "refresh_token" if refresh_token:
                jwt = self.verify_refresh_token(refresh_token)
                user_email = jwt["email"]
                user_id = jwt["sub"]
                user_name = jwt["name"]
            case _:
                raise ValueError(f"Invalid grant type: {grant_type}")
        access_token = self.create_jwt(
            user_id=str(user_id),
            name=user_name,
            email=user_email,
            exp=access_token_expiry(),
        )
        refresh_token = self.create_jwt(
            user_id=str(user_id),
            name=user_name,
            email=user_email,
            exp=refresh_token_expiry(),
        )
        return {"access_token": access_token, "refresh_token": refresh_token}


if __name__ == "__main__":
    print(AuthService.oauth_client)
