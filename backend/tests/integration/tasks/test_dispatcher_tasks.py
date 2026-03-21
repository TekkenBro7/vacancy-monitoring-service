import datetime
from collections.abc import Generator
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery.tasks.dispatcher_tasks import _dispatch_source_parse_tasks
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


@pytest.fixture
def patch_session_maker(db_session: AsyncSession) -> Generator[None, None, None]:
    class FakeSessionContext:
        async def __aenter__(self) -> AsyncSession:
            return db_session

        async def __aexit__(self, *args: object) -> None:
            pass

    with patch(
        "src.core.celery.tasks.dispatcher_tasks.async_session_maker",
        return_value=FakeSessionContext(),
    ):
        yield


@pytest.fixture
def mock_celery_task() -> Generator[MagicMock, None, None]:
    with patch("src.core.celery.tasks.dispatcher_tasks.run_source_parse_task") as mock_task:
        yield mock_task


@pytest.mark.asyncio
async def test_dispatches_pending_tasks(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task1 = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 14))
    task2 = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 15))
    db_session.add_all([task1, task2])
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)

    await _dispatch_source_parse_tasks()

    assert mock_celery_task.delay.call_count == 2
    mock_celery_task.delay.assert_any_call(task1.id)
    mock_celery_task.delay.assert_any_call(task2.id)


@pytest.mark.asyncio
async def test_skips_tasks_with_max_attempts(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task_ok = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 14), attempts=0)
    task_max = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 15), attempts=6)
    db_session.add_all([task_ok, task_max])
    await db_session.commit()
    await db_session.refresh(task_ok)

    await _dispatch_source_parse_tasks()

    assert mock_celery_task.delay.call_count == 1
    mock_celery_task.delay.assert_called_once_with(task_ok.id)


@pytest.mark.asyncio
async def test_skips_tasks_with_more_than_max_attempts(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 14), attempts=10)
    db_session.add(task)
    await db_session.commit()

    await _dispatch_source_parse_tasks()

    mock_celery_task.delay.assert_not_called()


@pytest.mark.asyncio
async def test_handles_empty_task_list(
    db_session: AsyncSession,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    await _dispatch_source_parse_tasks()

    mock_celery_task.delay.assert_not_called()


@pytest.mark.asyncio
async def test_dispatches_tasks_with_attempts_below_limit(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task1 = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 14), attempts=0)
    task2 = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 15), attempts=3)
    task3 = SourceParseTask(source_id=source.id, parse_date=date(2026, 2, 16), attempts=5)
    db_session.add_all([task1, task2, task3])
    await db_session.commit()

    await _dispatch_source_parse_tasks()

    assert mock_celery_task.delay.call_count == 3


@pytest.mark.asyncio
async def test_respects_limit(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    tasks = [
        SourceParseTask(
            source_id=source.id, parse_date=date(2026, 2, 14) + datetime.timedelta(days=i)
        )
        for i in range(250)
    ]
    db_session.add_all(tasks)
    await db_session.commit()

    await _dispatch_source_parse_tasks()

    assert mock_celery_task.delay.call_count == 200


@pytest.mark.asyncio
async def test_skips_success_tasks(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task = SourceParseTask(
        source_id=source.id,
        parse_date=date(2026, 2, 14),
        status="success",
    )
    db_session.add(task)
    await db_session.commit()

    await _dispatch_source_parse_tasks()

    mock_celery_task.delay.assert_not_called()


@pytest.mark.asyncio
async def test_skips_in_progress_tasks(
    db_session: AsyncSession,
    source: Source,
    patch_session_maker: None,
    mock_celery_task: MagicMock,
) -> None:
    task = SourceParseTask(
        source_id=source.id,
        parse_date=date(2026, 2, 14),
        status="in_progress",
    )
    db_session.add(task)
    await db_session.commit()

    await _dispatch_source_parse_tasks()

    mock_celery_task.delay.assert_not_called()
