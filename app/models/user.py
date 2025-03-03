from datetime import datetime
from typing import Optional, Self

import strawberry
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UserCreate(BaseModel):
    email: str
    name: str


class User(UserCreate):
    id: int

    @classmethod
    def from_user_create(cls, user: UserCreate, id: int) -> Self:
        return cls(id=id, email=user.email, name=user.name)

    @classmethod
    def from_jwt_payload(cls, payload: dict) -> Self:
        return cls(id=int(payload["sub"]), name=payload["name"], email=payload["email"])

    model_config = ConfigDict(from_attributes=True)


@strawberry.experimental.pydantic.type(name="User", model=User, all_fields=True)
class UserGQL:
    pass


class Base(DeclarativeBase):
    pass


class UserDb(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[Optional[datetime]]


class Session(BaseModel):
    user_id: int
    token: str
    invalidated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SessionDb(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    token: Mapped[str]
    invalidated_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[Optional[datetime]]
