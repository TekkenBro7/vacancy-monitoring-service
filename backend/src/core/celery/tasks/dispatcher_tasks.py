import asyncio

from src.core.celery.celery_app import celery_app
from src.core.celery.tasks.parsing_tasks import run_source_parse_task
from src.core.logger import logger
from src.database.repositories.source_parse_task_repository import SourceParseTaskRepository
from src.database.session import async_session_maker
from src.models.sources import SourceParseTask


@celery_app.task(
    name="dispatch_source_parse_tasks",
    queue="parsing_queue",
)
def dispatch_source_parse_tasks() -> None:
    asyncio.run(_dispatch_source_parse_tasks())


async def _dispatch_source_parse_tasks() -> None:
    async with async_session_maker() as session:
        repo = SourceParseTaskRepository(SourceParseTask, session)

        tasks = await repo.get_tasks_for_dispatch(limit=200)

        scheduled_count = 0

        for task in tasks:
            if task.attempts >= 6:
                continue

            run_source_parse_task.delay(task.id)
            scheduled_count += 1

        logger.info("Dispatched %s tasks", scheduled_count)
