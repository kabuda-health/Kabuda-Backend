from fastapi import APIRouter

from app.dependencies import UserDep
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/whoami")
def whoami(user: UserDep) -> User:
    return user
