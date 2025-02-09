from fastapi import APIRouter

from app.dependencies import UserDep

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/whoami")
def whoami(user: UserDep):
    return user
