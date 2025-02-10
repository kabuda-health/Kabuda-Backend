from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str


class User(UserCreate):
    id: int

    @classmethod
    def from_user_create(cls, user: UserCreate, id: int):
        return cls(id=id, email=user.email, name=user.name)

    @classmethod
    def from_jwt_payload(cls, payload: dict):
        return cls(id=int(payload["sub"]), name=payload["name"], email=payload["email"])
