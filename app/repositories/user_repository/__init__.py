from typing import Optional, Protocol

from app.models.user import User, UserCreate

from .mem_user_repository import MemUserRepo


class UserRepo(Protocol):

    def get_user_by_id(self, user_id: int) -> Optional[User]: ...

    def get_user_by_email(self, email: str) -> Optional[User]: ...

    def create_user(self, user: UserCreate) -> User: ...


class MockUserRepo(UserRepo):

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User(id=user_id, name="Alice", email="alice@alice.com")

    def get_user_by_email(self, email: str) -> Optional[User]:
        return User(id=1, name="Alice", email=email)

    def create_user(self, user: UserCreate) -> User:
        return User(id=1, name=user.name, email=user.email)


__all__ = ["UserRepo", "MockUserRepo", "MemUserRepo"]
