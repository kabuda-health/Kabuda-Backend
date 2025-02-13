from typing import Optional, Protocol

from app.models.user import User, UserCreate

from .mem_user_repository import MemUserRepo
from .pg_user_repository import PgUserRepo


class UserRepo(Protocol):

    async def get_user_by_id(self, user_id: int) -> Optional[User]: ...

    async def get_user_by_email(self, email: str) -> Optional[User]: ...

    async def create_user(self, user: UserCreate) -> User: ...


class MockUserRepo(UserRepo):

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User(id=user_id, name="Alice", email="alice@alice.com")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return User(id=1, name="Alice", email=email)

    async def create_user(self, user: UserCreate) -> User:
        return User(id=1, name=user.name, email=user.email)


__all__ = ["UserRepo", "MockUserRepo", "MemUserRepo", "PgUserRepo"]
