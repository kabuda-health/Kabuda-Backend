from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Optional, Protocol, Self

from app.models.user import Session, User, UserCreate

from .mem_user_repository import MemUserRepo
from .pg_user_repository import PgUserRepo


class UserRepo(Protocol):
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[Self]:
        yield self

    async def get_user_by_id(self, user_id: int) -> Optional[User]: ...
    async def get_user_by_email(self, email: str) -> Optional[User]: ...
    async def create_user(self, user: UserCreate) -> User: ...
    async def create_session(self, user_id: int, session_id: str) -> str: ...
    async def invalidate_active_sessions(self, user_id: int) -> None: ...
    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]: ...


class UserRepoService:
    def __init__(self, repo_getter: Callable[[], UserRepo]) -> None:
        self.repo_getter = repo_getter

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.transaction() as tx:
            return await tx.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.transaction() as tx:
            return await tx.get_user_by_email(email)

    async def create_user(self, user: UserCreate) -> User:
        async with self.transaction() as tx:
            return await tx.create_user(user)

    async def create_session(self, user_id: int, session_id: str) -> str:
        async with self.transaction() as tx:
            return await tx.create_session(user_id, session_id)

    async def invalidate_active_sessions(self, user_id: int) -> None:
        async with self.transaction() as tx:
            return await tx.invalidate_active_sessions(user_id)

    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]:
        async with self.transaction() as tx:
            return await tx.get_session(user_id, session_id)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[UserRepo]:
        async with self.repo_getter().transaction() as tx:
            yield tx


class MockUserRepo:
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[Self]:
        yield self

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


__all__ = ["UserRepo", "MockUserRepo", "MemUserRepo", "PgUserRepo", "UserRepoService"]
