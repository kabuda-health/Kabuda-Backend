from typing import AsyncGenerator, Callable, Generator

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from alembic import command
from alembic.config import Config
from app.clients.oauth import MockOAuthClient, OAuthClient
from app.dependencies import AuthService, PgUserRepo, get_auth_service
from app.main import app
from app.repositories.user_repository import UserRepo


@fixture
def oauth_client() -> OAuthClient:
    return MockOAuthClient()


@fixture(scope="session")
def pg_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:15") as container:
        connection_url = container.get_connection_url(driver=None)
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", connection_url)
        command.upgrade(config, "head")
        yield container


@fixture
def pg_engine(pg_container) -> AsyncEngine:
    connection_url = pg_container.get_connection_url(driver="asyncpg")
    return create_async_engine(
        connection_url,
        poolclass=NullPool,
        pool_pre_ping=True,
    )


@fixture
def user_repo(pg_engine) -> UserRepo:
    return PgUserRepo(pg_engine)


@fixture
def auth_service(user_repo, oauth_client) -> AuthService:
    return AuthService(user_repo, oauth_client)


@fixture
def api_server(auth_service: AuthService) -> FastAPI:
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    return app


@fixture
def api_server_builder(auth_service: AuthService) -> Callable[[bool], FastAPI]:
    def _api_server_builder(randomize_user: bool = False) -> FastAPI:
        if randomize_user:
            assert isinstance(auth_service.oauth_client, MockOAuthClient)
            auth_service.oauth_client.randomize = True
        app.dependency_overrides[get_auth_service] = lambda: auth_service
        return app

    return _api_server_builder


@fixture
async def test_client(api_server: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=api_server),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@fixture
def test_client_builder(
    api_server_builder: Callable[[bool], FastAPI],
) -> Callable[[bool], AsyncClient]:
    def _test_client_builder(
        randomize_user: bool,
    ) -> AsyncClient:
        return AsyncClient(
            transport=ASGITransport(app=api_server_builder(randomize_user)),
            base_url="http://test",
            follow_redirects=True,
        )

    return _test_client_builder
