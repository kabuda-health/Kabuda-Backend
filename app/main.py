import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from loguru import logger
from starlette.middleware.sessions import SessionMiddleware

from .routes import api_router, graphql_router
from .settings import Env, settings

app = FastAPI()
app.include_router(api_router)
app.include_router(graphql_router)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/")
def root():
    return {"Hello": "World"}


if __name__ == "__main__":
    logger.info(f"Starting '{settings.env}' server on {settings.host}:{settings.port}")
    if settings.env == Env.PROD:
        app.add_middleware(HTTPSRedirectMiddleware)
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "dev",
    )
