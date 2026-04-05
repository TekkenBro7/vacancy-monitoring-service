import asyncio
from typing import Any

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.database.session import async_session_maker
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.factories.import_service_factory import ImportServiceFactory


@celery_app.task(
    name="import_vacancies_batch",
    queue="import_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def import_vacancies_batch(
    vacancies_data: list[dict[str, Any]],
    source_name: str,
) -> None:
    asyncio.run(_import_vacancies_batch(vacancies_data, source_name))


async def _import_vacancies_batch(
    vacancies_data: list[dict[str, Any]],
    source_name: str,
) -> None:
    try:
        vacancies = [ParserVacancyResult.from_dict(v) for v in vacancies_data]

        async with async_session_maker() as session:
            import_service = ImportServiceFactory.create(session)

            await import_service.import_batch(vacancies, source_name)

            logger.info("Imported batch with %s vacancies, source: %s", len(vacancies), source_name)
    except Exception:
        logger.exception("Failed to import batch (%s vacancies)", len(vacancies_data))
