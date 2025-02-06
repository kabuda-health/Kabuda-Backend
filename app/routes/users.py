import arrow
from fastapi import APIRouter
from pydantic import BaseModel

from app.auth import AuthDep, create_jwt, get_user_id

router = APIRouter(prefix="/users", tags=["users"])


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(
    payload: LoginPayload,
):
    access_token = create_jwt(
        subject=str(get_user_id(payload.username)),
        name=payload.username,
        exp=arrow.utcnow().shift(minutes=15),
    )
    refresh_token = create_jwt(
        subject=str(get_user_id(payload.username)),
        name=payload.username,
        exp=arrow.utcnow().shift(days=7),
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/check-token")
def check_token(jwt: AuthDep):
    return jwt
