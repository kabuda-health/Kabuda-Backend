from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["dev", "prod"]

    host: str
    port: int

    secret_key: str

    google_auth_client_id: str
    google_auth_client_secret: str

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str


settings = Settings(_env_file=".env")  # pyright: ignore[reportCallIssue]
