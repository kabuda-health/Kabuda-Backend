from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["dev", "prod"]

    host: str
    port: int


settings = Settings(_env_file=".env")  # pyright: ignore[reportCallIssue]
