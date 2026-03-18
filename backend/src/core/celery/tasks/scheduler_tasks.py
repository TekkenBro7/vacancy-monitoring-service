import asyncio
from datetime import UTC, date, datetime, timedelta

from src.core.celery.celery_app import celery_app
from src.core.celery.tasks.parsing_tasks import run_source_parse_task
from src.core.logger import logger
from src.database.repositories.source_parse_task_repository import SourceParseTaskRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.session import async_session_maker
from src.models.sources import Source, SourceParseTask

START_PARSE_DATE = date(2026, 1, 1)
START_PARSE_DATE = date(2026, 2, 14)


@celery_app.task(name="schedule_source_parse_tasks", queue="parsing_queue")
def schedule_source_parse_tasks() -> None:
    logger.info("11111111111111111")
    asyncio.run(_schedule_source_parse_tasks())


async def _schedule_source_parse_tasks() -> None:
    today = datetime.now(UTC).date()
    last_full_day = today - timedelta(days=1)

    last_full_day = date(2026, 2, 17)

    if last_full_day < START_PARSE_DATE:
        logger.info(
            "No full days available for scheduling yet. start_date=%s, last_full_day=%s",
            START_PARSE_DATE,
            last_full_day,
        )
        return

    async with async_session_maker() as session:
        source_repo = SourceRepository(Source, session)
        parse_task_repo = SourceParseTaskRepository(SourceParseTask, session)

        sources = await source_repo.list()
        scheduled_count = 0

        for source in sources:
            missing_dates = await parse_task_repo.get_missing_dates_for_source(
                source_id=source.id,
                start_date=START_PARSE_DATE,
                end_date=last_full_day,
            )

            if not missing_dates:
                logger.info("Source %s: no missing dates", source.name)
                continue

            logger.info(
                "Source %s: found %s missing dates in range %s - %s",
                source.name,
                len(missing_dates),
                START_PARSE_DATE,
                last_full_day,
            )

            for parse_date in missing_dates:
                parse_task = await parse_task_repo.create_if_not_exists(
                    source_id=source.id,
                    parse_date=parse_date,
                )

                if parse_task.status == "pending":
                    run_source_parse_task.delay(parse_task.id)
                    scheduled_count += 1

        logger.info("Scheduled %s source parse tasks", scheduled_count)
