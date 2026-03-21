from collections.abc import Generator
from datetime import timedelta
from unittest.mock import patch

import pytest
import pytest_asyncio
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery.tasks.scheduler_tasks import (
    START_PARSE_DATE,
    _schedule_source_parse_tasks,
)
from src.models.sources import Source, SourceParseTask, SourceType


@pytest_asyncio.fixture
async def source_type(db_session: AsyncSession) -> SourceType:
    source_type = SourceType(type_name="API", description="Test API")
    db_session.add(source_type)
    await db_session.commit()
    await db_session.refresh(source_type)
    return source_type


@pytest_asyncio.fixture
async def source(db_session: AsyncSession, source_type: SourceType) -> Source:
    source = Source(
        name="HeadHunter",
        source_url="https://hh.ru",
        source_type_id=source_type.id,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def two_sources(db_session: AsyncSession, source_type: SourceType) -> list[Source]:
    sources = [
        Source(name="HeadHunter", source_url="https://hh.ru", source_type_id=source_type.id),
        Source(name="SuperJob", source_url="https://superjob.ru", source_type_id=source_type.id),
    ]
    db_session.add_all(sources)
    await db_session.commit()
    for s in sources:
        await db_session.refresh(s)
    return sources


async def get_all_tasks(db_session: AsyncSession) -> list[SourceParseTask]:
    result = await db_session.execute(select(SourceParseTask))
    return list(result.scalars().all())


@pytest.fixture
def patch_session_maker(db_session: AsyncSession) -> Generator[None, None, None]:
    class FakeSessionContext:
        async def __aenter__(self) -> AsyncSession:
            return db_session

        async def __aexit__(self, *args: object) -> None:
            pass

    with patch(
        "src.core.celery.tasks.scheduler_tasks.async_session_maker",
        return_value=FakeSessionContext(),
    ):
        yield


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE)
async def test_skips_when_no_full_days_available(db_session: AsyncSession, source: Source) -> None:
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)
    assert len(tasks) == 0


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=3))
async def test_creates_tasks_for_missing_dates(
    db_session: AsyncSession, source: Source, patch_session_maker: None
) -> None:
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)

    assert len(tasks) == 3

    task_dates = [task.parse_date for task in tasks]
    expected_dates = [
        START_PARSE_DATE,
        START_PARSE_DATE + timedelta(days=1),
        START_PARSE_DATE + timedelta(days=2),
    ]
    assert task_dates == expected_dates

    assert all(task.source_id == source.id for task in tasks)


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=3))
async def test_skips_already_existing_tasks(
    db_session: AsyncSession, source: Source, patch_session_maker: None
) -> None:
    existing_task = SourceParseTask(
        source_id=source.id,
        parse_date=START_PARSE_DATE,
    )
    db_session.add(existing_task)
    await db_session.commit()

    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)

    assert len(tasks) == 3


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=2))
async def test_processes_multiple_sources(
    db_session: AsyncSession, two_sources: list[Source], patch_session_maker: None
) -> None:
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)

    assert len(tasks) == 4

    source_ids = {task.source_id for task in tasks}
    expected_ids = {s.id for s in two_sources}
    assert source_ids == expected_ids


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=2))
async def test_handles_empty_sources(db_session: AsyncSession) -> None:
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)
    assert len(tasks) == 0


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=10))
async def test_calculates_correct_date_range(
    db_session: AsyncSession, source: Source, patch_session_maker: None
) -> None:
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)

    assert len(tasks) == 10

    task_dates = sorted(task.parse_date for task in tasks)
    expected_last_date = START_PARSE_DATE + timedelta(days=9)

    assert task_dates[0] == START_PARSE_DATE
    assert task_dates[-1] == expected_last_date


@pytest.mark.asyncio
@freeze_time(START_PARSE_DATE + timedelta(days=3))
async def test_idempotent_multiple_runs(
    db_session: AsyncSession, source: Source, patch_session_maker: None
) -> None:
    await _schedule_source_parse_tasks()
    await _schedule_source_parse_tasks()
    await _schedule_source_parse_tasks()

    tasks = await get_all_tasks(db_session)
    assert len(tasks) == 3
