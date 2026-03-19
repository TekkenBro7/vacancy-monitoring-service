import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.router import api_router
from src.core.celery.tasks.scheduler_tasks import schedule_source_parse_tasks
from src.core.config import base_config
from src.core.logger import logger
from src.core.rabbitmq import RabbitMQ
from src.core.redis_client import redis_client
from src.database.session import async_session_maker

app = FastAPI(
    title="Improved API Service",
    description="API service for manage users and transactions",
    version="0.0.1",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=base_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=base_config.CORS_METHODS,
    allow_headers=base_config.CORS_HEADERS,
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    async def check_rabbitmq() -> None:
        try:
            await RabbitMQ.connect()
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.exception(
                "RabbitMQ connection failed error=%s",
                e,
            )

    async def check_postgres() -> None:
        try:
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
            logger.info("Postgres connection established")
        except Exception as e:
            logger.exception(
                "Postgres connection failed error=%s",
                e,
            )

    async def check_redis() -> None:
        try:
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.exception(
                "Redis connection failed error=%s",
                e,
            )

    await asyncio.gather(
        check_rabbitmq(),
        check_postgres(),
        check_redis(),
    )

    logger.info("Application startup complete")

    schedule_source_parse_tasks.delay()
    from src.core.celery.tasks import dispatch_source_parse_tasks

    dispatch_source_parse_tasks.delay()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    try:
        await RabbitMQ.close()
        logger.info("RabbitMQ connection closed")
    except Exception as exc:
        logger.exception(
            "RabbitMQ shutdown failed error=%s",
            exc,
        )

    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as exc:
        logger.exception(
            "Redis shutdown failed error=%s",
            exc,
        )

    logger.info("Application shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=base_config.HOST,
        port=base_config.PORT,
        reload=base_config.RELOAD,
    )
