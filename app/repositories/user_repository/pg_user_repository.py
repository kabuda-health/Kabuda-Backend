from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.models.user import Session, SessionDb, User, UserCreate, UserDb


class PgUserRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.existing_transaction: Optional[AsyncConnection] = None

    @asynccontextmanager
    async def transaction(self):
        async with self.engine.begin() as conn:
            self.existing_transaction = conn
            yield
            self.existing_transaction = None

    @asynccontextmanager
    async def get_transaction(self):
        if self.existing_transaction is not None:
            logger.info("Using existing transaction")
            yield self.existing_transaction
        else:
            logger.info("Creating new transaction")
            async with self.engine.begin() as conn:
                yield conn

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.get_transaction() as conn:
            stmt = select(UserDb).where(UserDb.id == user_id)
            result = await conn.execute(stmt)
            user = result.fetchone()
            if user is not None:
                return User.model_validate(user)
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.get_transaction() as conn:
            stmt = select(UserDb).where(UserDb.email == email)
            result = await conn.execute(stmt)
            user = result.first()
            if user is not None:
                return User.model_validate(user)
            return None

    async def create_user(self, user: UserCreate) -> User:
        async with self.get_transaction() as conn:
            stmt = insert(UserDb).values(**user.model_dump()).returning(UserDb)
            result = await conn.execute(stmt)
            created_user = result.one()
            return User.model_validate(created_user)

    async def create_session(self, user_id: int, session_id: str) -> str:
        async with self.get_transaction() as conn:
            stmt = (
                insert(SessionDb)
                .values(user_id=user_id, token=session_id)
                .returning(SessionDb.token)
            )
            await conn.execute(stmt)
            return session_id

    async def invalidate_active_sessions(self, user_id: int) -> None:
        async with self.get_transaction() as conn:
            stmt = (
                update(SessionDb)
                .where(
                    SessionDb.user_id == user_id,
                    SessionDb.deleted_at == None,  # noqa
                    SessionDb.invalidated_at == None,  # noqa
                )
                .values(invalidated_at=datetime.now(timezone.utc).replace(tzinfo=None))
            )
            await conn.execute(stmt)

    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]:
        async with self.get_transaction() as conn:
            stmt = select(SessionDb).where(
                SessionDb.user_id == user_id,
                SessionDb.token == session_id,
            )
            result = await conn.execute(stmt)
            session = result.first()
            if session is not None:
                return Session.model_validate(session)
            return None

    async def commit(self):
        async with self.get_transaction() as conn:
            await conn.commit()
