from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.models.user import Session, SessionDb, User, UserCreate, UserDb


class PgUserRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.async_session_maker = async_sessionmaker(engine)
        self.existing_transaction: Optional[AsyncSession] = None

    @asynccontextmanager
    async def transaction(self):
        try:
            assert self.existing_transaction is None
            logger.info("Creating new transaction")
            async with self.async_session_maker() as conn:
                async with conn.begin():
                    self.existing_transaction = conn
                    yield
        finally:
            self.existing_transaction = None

    @asynccontextmanager
    async def get_transaction(self):
        if self.existing_transaction is not None:
            logger.info("Using existing transaction")
            yield self.existing_transaction
        else:
            async with self.transaction():
                assert self.existing_transaction is not None
                yield self.existing_transaction

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.get_transaction() as conn:
            stmt = (
                select(UserDb)
                .where(UserDb.id == user_id, UserDb.deleted_at.is_(None))
                .limit(1)
            )
            user = await conn.scalar(stmt)
            if user is not None:
                user = User.model_validate(user)
            return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.get_transaction() as conn:
            stmt = (
                select(UserDb)
                .where(
                    UserDb.email == email,
                    UserDb.deleted_at.is_(None),
                )
                .limit(1)
            )
            user = await conn.scalar(stmt)
            if user is not None:
                user = User.model_validate(user)
            return user

    async def create_user(self, user: UserCreate) -> User:
        async with self.get_transaction() as conn:
            stmt = insert(UserDb).values(**user.model_dump()).returning(UserDb)
            created_user = await conn.scalar(stmt)
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
                    SessionDb.deleted_at.is_(None),
                    SessionDb.invalidated_at.is_(None),
                )
                .values(invalidated_at=datetime.now(timezone.utc).replace(tzinfo=None))
            )
            await conn.execute(stmt)

    async def get_session(self, user_id: int, session_id: str) -> Optional[Session]:
        async with self.get_transaction() as conn:
            stmt = (
                select(SessionDb)
                .where(
                    SessionDb.user_id == user_id,
                    SessionDb.token == session_id,
                    SessionDb.deleted_at.is_(None),
                )
                .limit(1)
            )
            session = await conn.scalar(stmt)
            if session is not None:
                session = Session.model_validate(session)
            return session

    async def commit(self):
        async with self.get_transaction() as conn:
            await conn.commit()
