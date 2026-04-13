import asyncio
from datetime import UTC, datetime, time, timedelta

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.database.repositories.source_parse_task_repository import SourceParseTaskRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.session import async_session_maker
from src.models.sources import Source, SourceParseTask
from src.parsers.factories.import_service_factory import ImportServiceFactory
from src.parsers.factories.vacancy_service_factory import VacancyServiceFactory


@celery_app.task(name="run_source_parse_task", queue="parsing_queue")
def run_source_parse_task(task_id: int) -> None:
    asyncio.run(_run_source_parse_task(task_id))


async def _run_source_parse_task(task_id: int) -> None:
    async with async_session_maker() as session:
        parse_task_repo = SourceParseTaskRepository(SourceParseTask, session)
        source_repo = SourceRepository(Source, session)

        task = await parse_task_repo.get_by_id(task_id)
        if task is None:
            logger.warning("Source parse task %s not found", task_id)
            return

        if task.status not in {"pending", "failed"}:
            logger.info(
                "Task %s skipped because status is %s",
                task.id,
                task.status,
            )
            return

        source = await source_repo.get_by_id(task.source_id)

        if source.name != "Telegram":
            return

        if source is None:
            await parse_task_repo.mark_failed(task.id, f"Source {task.source_id} not found")
            return

        await parse_task_repo.mark_in_progress(task.id)

        try:
            date_from = datetime.combine(task.parse_date, time.min, tzinfo=UTC)
            date_to = date_from + timedelta(days=1)

            import_service = ImportServiceFactory.create(session)
            parser_service = VacancyServiceFactory.create(source.name, import_service)

            await parser_service.run(
                query=None,
                from_date=date_from,
                to_date=date_to,
            )

            await parse_task_repo.mark_success(task.id)

            logger.info(
                "Source parse task %s completed successfully for source=%s date=%s",
                task.id,
                source.name,
                task.parse_date,
            )

        except Exception as e:
            logger.exception("Source parse task %s failed", task.id)
            await parse_task_repo.mark_failed(task.id, str(e))
