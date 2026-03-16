from datetime import UTC, datetime, timedelta
import asyncio

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.source_parse_task_repository import SourceParseTaskRepository
from src.database.session import async_session_maker
from src.core.celery.tasks.parsing_tasks import run_source_parse_task


@celery_app.task(name="schedule_source_parse_tasks", queue="parsing_queue")
def schedule_source_parse_tasks() -> None:
    asyncio.run(_schedule_source_parse_tasks())


async def _schedule_source_parse_tasks() -> None:
    today = datetime.now(UTC).date()

    async with async_session_maker() as session:
        source_repo = SourceRepository(session)
        parse_task_repo = SourceParseTaskRepository(session)

        sources = await source_repo.list()
        created_count = 0

        for source in sources:
            if source.last_successful_parse_date is None:
                logger.info(
                    "Source %s has no last_successful_parse_date, skipping",
                    source.name,
                )
                continue

            current_date = source.last_successful_parse_date + timedelta(days=1)

            while current_date <= today:
                parse_task = await parse_task_repo.create_if_not_exists(
                    source_id=source.id,
                    parse_date=current_date,
                )

                if parse_task.status == "pending":
                    run_source_parse_task.delay(parse_task.id)
                    created_count += 1

                current_date += timedelta(days=1)

        logger.info("Scheduled %s source parse tasks", created_count)