from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy.ext.asyncio import create_async_engine
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
def pg_container():
    with PostgresContainer("postgres:15") as container:
        connection_url = container.get_connection_url(driver=None)
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", connection_url)
        command.upgrade(config, "head")
        yield container


@fixture
def pg_engine(pg_container):
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
def test_client(auth_service: AuthService) -> TestClient:
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    return TestClient(app)
