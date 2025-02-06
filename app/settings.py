from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["dev", "prod"]

    host: str
    port: int

    secret_key: str


settings = Settings(_env_file=".env")  # pyright: ignore[reportCallIssue]
