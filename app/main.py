import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from loguru import logger
from starlette.middleware.sessions import SessionMiddleware

from .routes import api_router
from .routes.graphql import graphql_router
from .settings import settings

app = FastAPI()
app.include_router(api_router)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(graphql_router)

@app.get("/")
def root():
    return {"Hello": "World"}

if __name__ == "__main__":
    logger.info(f"Starting '{settings.env}' server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "dev",
    )
