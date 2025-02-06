from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    return {"access_token": "fake_access_token", "refresh_token": "fake_refresh_token"}
