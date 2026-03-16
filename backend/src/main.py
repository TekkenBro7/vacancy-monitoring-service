import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.router import api_router
from src.core.config import base_config
from src.core.logger import logger
from src.core.rabbitmq import RabbitMQ
from src.core.redis_client import redis_client
from src.database.session import async_session_maker
from src.parsers.services.parser_import_service import ParserImportService

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

    from datetime import datetime

    from src.database.repositories.city_repository import CityRepository
    from src.database.repositories.company_repository import CompanyRepository
    from src.database.repositories.currency_repository import CurrencyRepository
    from src.database.repositories.source_repository import SourceRepository
    from src.database.repositories.vacancy_repository import VacancyRepository
    from src.parsers.hh_ru.hh_service import HHVacancyService

    async with async_session_maker() as session:
        from src.models.companies import Company, Vacancy
        from src.models.currencies import Currency
        from src.models.locations import City
        from src.models.sources import Source

        vacancy_repo = VacancyRepository(Vacancy, session)
        company_repo = CompanyRepository(Company, session)
        city_repo = CityRepository(City, session)
        currency_repo = CurrencyRepository(Currency, session)
        source_repo = SourceRepository(Source, session)

        import_service = ParserImportService(
            vacancy_repo=vacancy_repo,
            company_repo=company_repo,
            city_repo=city_repo,
            currency_repo=currency_repo,
            source_repo=source_repo,
        )

        service = HHVacancyService(import_service=import_service)

        #start = datetime(2026, 2, 12, 0, 0)
        #end = datetime(2026, 2, 13, 0, 0)

        await service.run(None)


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
