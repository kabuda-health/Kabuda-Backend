from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.user import User, UserCreate, UserDb


class PgUserRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.engine.begin() as conn:
            stmt = select(UserDb).where(UserDb.id == user_id)
            result = await conn.execute(stmt)
            user = result.fetchone()
            if user is not None:
                return User.model_validate(user)
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.engine.begin() as conn:
            stmt = select(UserDb).where(UserDb.email == email)
            result = await conn.execute(stmt)
            user = result.first()
            if user is not None:
                return User.model_validate(user)
            return None

    async def create_user(self, user: UserCreate) -> User:
        async with self.engine.begin() as conn:
            stmt = insert(UserDb).values(**user.model_dump()).returning(UserDb)
            result = await conn.execute(stmt)
            created_user = result.one()
            return User.model_validate(created_user)
