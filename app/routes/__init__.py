from fastapi import APIRouter

from .auth import router as auth_router
from .graphql import router as graphql_router
from .users import router as users_router

api_router = APIRouter(prefix="/api")

api_router.include_router(users_router)
api_router.include_router(auth_router)

__all__ = ["api_router", "graphql_router"]
