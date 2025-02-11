from typing import Optional

from app.models.user import User, UserCreate


class MemUserRepo:
    def __init__(self) -> None:
        self.next_id = 2
        self.users_by_id: dict[int, User] = {}
        self.users_by_email: dict[str, User] = {}

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users_by_id.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return self.users_by_email.get(email)

    async def create_user(self, user: UserCreate) -> User:
        user = User(id=self.next_id, name=user.name, email=user.email)
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        self.next_id += 1
        return user
