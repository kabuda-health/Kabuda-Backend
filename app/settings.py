from enum import StrEnum, auto

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    DEV = auto()
    PROD = auto()


class Settings(BaseSettings):
    env: Env

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

    model_config = SettingsConfigDict(env_prefix="kabuda_backend_", env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
