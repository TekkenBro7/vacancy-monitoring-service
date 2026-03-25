import asyncio
from datetime import UTC, date, datetime, timedelta

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.database.repositories.source_parse_task_repository import SourceParseTaskRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.session import async_session_maker
from src.models.sources import Source, SourceParseTask

START_PARSE_DATE = date(2026, 3, 19)


@celery_app.task(name="schedule_source_parse_tasks", queue="parsing_queue")
def schedule_source_parse_tasks() -> None:
    asyncio.run(_schedule_source_parse_tasks())


async def _schedule_source_parse_tasks() -> None:
    today = datetime.now(UTC).date()
    last_full_day = today - timedelta(days=1)

    last_full_day = date(2026, 3, 19)

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
        created_count = 0

        for source in sources:
            try:
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
                    await parse_task_repo.create_if_not_exists(
                        source_id=source.id,
                        parse_date=parse_date,
                    )

                    created_count += 1

            except Exception:
                logger.exception("Failed processing source %s", source.name)
                continue

        logger.info("Scheduled %s source parse tasks", created_count)
