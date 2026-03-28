import datetime
from collections.abc import Generator
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery.tasks.parsing_tasks import _run_source_parse_task
from src.core.config import hh_config
from src.models.sources import Source, SourceParseTask, SourceType


@pytest_asyncio.fixture
async def source_type(db_session: AsyncSession) -> SourceType:
    source_type = SourceType(type_name="API", description="Test API")
    db_session.add(source_type)
    await db_session.commit()
    await db_session.refresh(source_type)
    return source_type


@pytest_asyncio.fixture
async def hh_source(db_session: AsyncSession, source_type: SourceType) -> Source:
    source = Source(
        name=hh_config.HH_SOURCE_NAME,
        source_url="https://hh.ru",
        source_type_id=source_type.id,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def unsupported_source(db_session: AsyncSession, source_type: SourceType) -> Source:
    source = Source(
        name="UnsupportedSource",
        source_url="https://example.com",
        source_type_id=source_type.id,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def pending_task(db_session: AsyncSession, hh_source: Source) -> SourceParseTask:
    task = SourceParseTask(
        source_id=hh_source.id,
        parse_date=date(2026, 2, 14),
        status="pending",
        attempts=0,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def failed_task(db_session: AsyncSession, hh_source: Source) -> SourceParseTask:
    task = SourceParseTask(
        source_id=hh_source.id,
        parse_date=date(2026, 2, 15),
        status="failed",
        attempts=2,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
def patch_session_maker(db_session: AsyncSession) -> Generator[None, None, None]:
    class FakeSessionContext:
        async def __aenter__(self) -> AsyncSession:
            return db_session

        async def __aexit__(self, *args: object) -> None:
            pass

    with patch(
        "src.core.celery.tasks.parsing_tasks.async_session_maker",
        return_value=FakeSessionContext(),
    ):
        yield


@pytest.fixture
def mock_vacancy_service() -> Generator[MagicMock, None, None]:
    """Мокаем VacancyServiceFactory.create чтобы возвращал мок сервиса"""
    mock_service_instance = AsyncMock()
    with patch(
        "src.core.celery.tasks.parsing_tasks.VacancyServiceFactory.create",
        return_value=mock_service_instance,
    ) as mock_factory:
        # Добавляем ссылку на мок-инстанс для проверок
        mock_factory.mock_service = mock_service_instance
        yield mock_factory


@pytest.fixture
def mock_import_factory() -> Generator[MagicMock, None, None]:
    """Мокаем ImportServiceFactory.create"""
    with patch(
        "src.core.celery.tasks.parsing_tasks.ImportServiceFactory.create",
        return_value=MagicMock(),
    ) as mock_factory:
        yield mock_factory


async def get_task_by_id(db_session: AsyncSession, task_id: int) -> SourceParseTask | None:
    result = await db_session.execute(select(SourceParseTask).where(SourceParseTask.id == task_id))
    return result.scalar_one_or_none()


@pytest.mark.asyncio
async def test_task_not_found(
    db_session: AsyncSession,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
) -> None:
    await _run_source_parse_task(task_id=99999)

    mock_vacancy_service.mock_service.run.assert_not_called()


@pytest.mark.asyncio
async def test_skips_success_status(
    db_session: AsyncSession,
    hh_source: Source,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
) -> None:
    task = SourceParseTask(
        source_id=hh_source.id,
        parse_date=date(2026, 2, 14),
        status="success",
        attempts=1,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    await _run_source_parse_task(task.id)

    mock_vacancy_service.mock_service.run.assert_not_called()


@pytest.mark.asyncio
async def test_skips_in_progress_status(
    db_session: AsyncSession,
    hh_source: Source,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
) -> None:
    task = SourceParseTask(
        source_id=hh_source.id,
        parse_date=date(2026, 2, 14),
        status="in_progress",
        attempts=1,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    await _run_source_parse_task(task.id)

    mock_vacancy_service.mock_service.run.assert_not_called()


@pytest.mark.asyncio
async def test_processes_pending_task_successfully(
    db_session: AsyncSession,
    pending_task: SourceParseTask,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
    mock_import_factory: MagicMock,
) -> None:
    await _run_source_parse_task(pending_task.id)

    mock_vacancy_service.mock_service.run.assert_called_once()

    updated_task = await get_task_by_id(db_session, pending_task.id)
    assert updated_task is not None
    assert updated_task.status == "success"
    assert updated_task.finished_at is not None


@pytest.mark.asyncio
async def test_processes_failed_task_successfully(
    db_session: AsyncSession,
    failed_task: SourceParseTask,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
    mock_import_factory: MagicMock,
) -> None:
    initial_attempts = failed_task.attempts

    await _run_source_parse_task(failed_task.id)

    mock_vacancy_service.mock_service.run.assert_called_once()

    updated_task = await get_task_by_id(db_session, failed_task.id)
    assert updated_task is not None
    assert updated_task.status == "success"
    assert updated_task.attempts == initial_attempts + 1


@pytest.mark.asyncio
async def test_marks_in_progress_before_parsing(
    db_session: AsyncSession,
    pending_task: SourceParseTask,
    patch_session_maker: None,
    mock_import_factory: MagicMock,
) -> None:
    captured_status: list[str] = []

    async def capture_status(*args: object, **kwargs: object) -> None:
        task = await get_task_by_id(db_session, pending_task.id)
        if task:
            captured_status.append(task.status)

    mock_service_instance = AsyncMock()
    mock_service_instance.run = capture_status

    with patch(
        "src.core.celery.tasks.parsing_tasks.VacancyServiceFactory.create",
        return_value=mock_service_instance,
    ):
        await _run_source_parse_task(pending_task.id)

    assert captured_status == ["in_progress"]


@pytest.mark.asyncio
async def test_marks_failed_on_parser_exception(
    db_session: AsyncSession,
    pending_task: SourceParseTask,
    patch_session_maker: None,
    mock_import_factory: MagicMock,
) -> None:
    mock_service_instance = AsyncMock()
    mock_service_instance.run.side_effect = RuntimeError("Connection timeout")

    with patch(
        "src.core.celery.tasks.parsing_tasks.VacancyServiceFactory.create",
        return_value=mock_service_instance,
    ):
        await _run_source_parse_task(pending_task.id)

    updated_task = await get_task_by_id(db_session, pending_task.id)
    assert updated_task is not None
    assert updated_task.status == "failed"
    assert "Connection timeout" in (updated_task.error_message or "")


@pytest.mark.asyncio
async def test_unsupported_source_marks_failed(
    db_session: AsyncSession,
    unsupported_source: Source,
    patch_session_maker: None,
    mock_import_factory: MagicMock,
) -> None:
    task = SourceParseTask(
        source_id=unsupported_source.id,
        parse_date=date(2026, 2, 14),
        status="pending",
        attempts=0,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Не мокаем VacancyServiceFactory — пусть выбросит реальную ошибку
    await _run_source_parse_task(task.id)

    updated_task = await get_task_by_id(db_session, task.id)
    assert updated_task is not None
    assert updated_task.status == "failed"
    assert "unsupported" in (updated_task.error_message or "").lower()


@pytest.mark.asyncio
async def test_increments_attempts_on_each_run(
    db_session: AsyncSession,
    pending_task: SourceParseTask,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
    mock_import_factory: MagicMock,
) -> None:
    initial_attempts = pending_task.attempts

    await _run_source_parse_task(pending_task.id)

    updated_task = await get_task_by_id(db_session, pending_task.id)
    assert updated_task is not None
    assert updated_task.attempts == initial_attempts + 1


@pytest.mark.asyncio
async def test_parser_called_with_correct_date_range(
    db_session: AsyncSession,
    pending_task: SourceParseTask,
    patch_session_maker: None,
    mock_vacancy_service: MagicMock,
    mock_import_factory: MagicMock,
) -> None:
    await _run_source_parse_task(pending_task.id)

    mock_vacancy_service.mock_service.run.assert_called_once()
    call_kwargs = mock_vacancy_service.mock_service.run.call_args.kwargs

    assert call_kwargs["query"] is None
    assert call_kwargs["from_date"].date() == pending_task.parse_date
    assert call_kwargs["to_date"].date() == call_kwargs["from_date"].date() + datetime.timedelta(
        days=1
    )
