from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Protocol, Self

from app.models.user import Session, User, UserCreate

from .mem_user_repository import MemUserRepo
from .pg_user_repository import PgUserRepo


class UserRepoInner(Protocol):
    async def get_user_by_id(self, user_id: int) -> Optional[User]: ...
    async def get_user_by_email(self, email: str) -> Optional[User]: ...
    async def create_user(self, user: UserCreate) -> User: ...
    async def create_session(self, user_id: int, session_id: str) -> str: ...
    async def invalidate_active_sessions(self, user_id: int) -> None: ...
    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]: ...


class TransactionRepo(Protocol):
    @asynccontextmanager
    def transaction(self) -> AsyncGenerator[Self]: ...


class UserRepo(UserRepoInner, TransactionRepo, Protocol):
    pass


class MockUserRepo:
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[Self]:
        yield type(self)()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User(id=user_id, name="Alice", email="alice@alice.com")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return User(id=1, name="Alice", email=email)

    async def create_user(self, user: UserCreate) -> User:
        return User(id=1, name=user.name, email=user.email)

    async def create_session(self, user_id: int, session_id: str) -> str:
        return session_id

    async def invalidate_active_sessions(self, user_id: int) -> None:
        pass

    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]:
        return Session(user_id=user_id, token=session_id, invalidated_at=None)


__all__ = ["UserRepo", "MockUserRepo", "MemUserRepo", "PgUserRepo"]
