import uvicorn
from fastapi import FastAPI
from loguru import logger

from .routes import api_router
from .settings import settings

app = FastAPI()
app.include_router(api_router)


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
