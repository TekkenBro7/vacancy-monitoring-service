from datetime import date, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.source_parse_task_repository import (
    SourceParseTaskRepository,
)
from src.models.sources import Source, SourceParseTask, SourceType


@pytest.fixture
def repo(db_session: AsyncSession) -> SourceParseTaskRepository:
    return SourceParseTaskRepository(SourceParseTask, db_session)


@pytest_asyncio.fixture
async def source_type(db_session: AsyncSession) -> SourceType:
    source_type = SourceType(type_name="API", description="Job board API")
    db_session.add(source_type)
    await db_session.commit()
    await db_session.refresh(source_type)
    return source_type


@pytest_asyncio.fixture
async def source(source_type: SourceType, db_session: AsyncSession) -> Source:
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
async def another_source(source_type: SourceType, db_session: AsyncSession) -> Source:
    source = Source(
        name="SuperJob",
        source_url="https://superjob.ru",
        source_type_id=source_type.id,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def parse_task(source: Source, db_session: AsyncSession) -> SourceParseTask:
    task = SourceParseTask(
        source_id=source.id,
        parse_date=date.today(),
        status="pending",
        attempts=0,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def multiple_tasks(source: Source, db_session: AsyncSession) -> list[SourceParseTask]:
    today = date.today()
    tasks_data = [
        {"parse_date": today - timedelta(days=5), "status": "success", "attempts": 1},
        {"parse_date": today - timedelta(days=4), "status": "failed", "attempts": 3},
        {"parse_date": today - timedelta(days=3), "status": "pending", "attempts": 0},
        {"parse_date": today - timedelta(days=2), "status": "in_progress", "attempts": 1},
        {"parse_date": today - timedelta(days=1), "status": "pending", "attempts": 0},
        {"parse_date": today, "status": "pending", "attempts": 0},
    ]

    tasks = []
    for data in tasks_data:
        task = SourceParseTask(
            source_id=source.id,
            parse_date=data["parse_date"],
            status=data["status"],
            attempts=data["attempts"],
        )
        db_session.add(task)
        tasks.append(task)

    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)

    return tasks


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_existing_task(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask
    ) -> None:
        result = await repo.get_by_id(parse_task.id)

        assert result is not None
        assert result.id == parse_task.id
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_returns_none_for_non_existing(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        result = await repo.get_by_id(99999)

        assert result is None


class TestGetBySourceAndDate:
    @pytest.mark.asyncio
    async def test_returns_existing_task(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask, source: Source
    ) -> None:
        result = await repo.get_by_source_and_date(source.id, parse_task.parse_date)

        assert result is not None
        assert result.id == parse_task.id

    @pytest.mark.asyncio
    async def test_returns_none_for_wrong_date(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask, source: Source
    ) -> None:
        wrong_date = parse_task.parse_date + timedelta(days=1)

        result = await repo.get_by_source_and_date(source.id, wrong_date)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_wrong_source(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask, another_source: Source
    ) -> None:
        result = await repo.get_by_source_and_date(another_source.id, parse_task.parse_date)

        assert result is None


class TestCreateIfNotExists:
    @pytest.mark.asyncio
    async def test_creates_new_task(self, repo: SourceParseTaskRepository, source: Source) -> None:
        task = await repo.create_if_not_exists(source.id, date(2024, 1, 1))

        assert task.id is not None
        assert task.source_id == source.id
        assert task.status == "pending"
        assert task.attempts == 0

    @pytest.mark.asyncio
    async def test_returns_existing_task(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        t1 = await repo.create_if_not_exists(source.id, date(2024, 1, 1))
        t2 = await repo.create_if_not_exists(source.id, date(2024, 1, 1))

        assert t1.id == t2.id

    @pytest.mark.asyncio
    async def test_creates_tasks_for_different_dates(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        t1 = await repo.create_if_not_exists(source.id, date(2024, 1, 1))
        t2 = await repo.create_if_not_exists(source.id, date(2024, 1, 2))

        assert t1.id != t2.id

    @pytest.mark.asyncio
    async def test_creates_tasks_for_different_sources(
        self, repo: SourceParseTaskRepository, source: Source, another_source: Source
    ) -> None:
        same_date = date(2024, 1, 1)

        t1 = await repo.create_if_not_exists(source.id, same_date)
        t2 = await repo.create_if_not_exists(another_source.id, same_date)

        assert t1.id != t2.id


class TestHasTasksForSource:
    @pytest.mark.asyncio
    async def test_returns_true_when_tasks_exist(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask, source: Source
    ) -> None:
        result = await repo.has_tasks_for_source(source.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_tasks(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        result = await repo.has_tasks_for_source(source.id)

        assert result is False


class TestGetExistingDatesForSource:
    @pytest.mark.asyncio
    async def test_returns_existing_dates(
        self, repo: SourceParseTaskRepository, multiple_tasks: list[SourceParseTask], source: Source
    ) -> None:
        today = date.today()

        result = await repo.get_existing_dates_for_source(
            source.id, today - timedelta(days=10), today
        )

        expected = {task.parse_date for task in multiple_tasks}
        assert result == expected

    @pytest.mark.asyncio
    async def test_returns_empty_for_wrong_range(
        self, repo: SourceParseTaskRepository, multiple_tasks: list[SourceParseTask], source: Source
    ) -> None:
        result = await repo.get_existing_dates_for_source(
            source.id, date.today() - timedelta(days=100), date.today() - timedelta(days=50)
        )

        assert result == set()


class TestGetMissingDatesForSource:
    @pytest.mark.asyncio
    async def test_returns_all_when_no_tasks(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        result = await repo.get_missing_dates_for_source(
            source.id, date(2024, 1, 1), date(2024, 1, 3)
        )

        assert result == [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]

    @pytest.mark.asyncio
    async def test_returns_empty_for_invalid_range(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        result = await repo.get_missing_dates_for_source(
            source.id, date(2024, 1, 5), date(2024, 1, 1)
        )

        assert result == []


class TestGetPendingTasks:
    @pytest.mark.asyncio
    async def test_returns_only_pending(
        self, repo: SourceParseTaskRepository, multiple_tasks: list[SourceParseTask]
    ) -> None:
        result = await repo.get_pending_tasks()

        for task in result:
            assert task.status == "pending"

    @pytest.mark.asyncio
    async def test_respects_limit(
        self, repo: SourceParseTaskRepository, multiple_tasks: list[SourceParseTask]
    ) -> None:
        result = await repo.get_pending_tasks(limit=2)

        assert len(result) <= 2


class TestGetTasksForDispatch:
    @pytest.mark.asyncio
    async def test_returns_pending_and_failed(
        self, repo: SourceParseTaskRepository, multiple_tasks: list[SourceParseTask]
    ) -> None:
        result = await repo.get_tasks_for_dispatch()

        for task in result:
            assert task.status in ["pending", "failed"]


class TestMarkInProgress:
    @pytest.mark.asyncio
    async def test_updates_status(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask
    ) -> None:
        result = await repo.mark_in_progress(parse_task.id)

        assert result.status == "in_progress"
        assert result.attempts == 1
        assert result.started_at is not None

    @pytest.mark.asyncio
    async def test_raises_for_non_existing(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        with pytest.raises(ValueError, match="Task 99999 not found"):
            await repo.mark_in_progress(99999)


class TestMarkSuccess:
    @pytest.mark.asyncio
    async def test_updates_status(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask
    ) -> None:
        result = await repo.mark_success(parse_task.id)

        assert result.status == "success"
        assert result.finished_at is not None

    @pytest.mark.asyncio
    async def test_raises_for_non_existing(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        with pytest.raises(ValueError, match="Task 99999 not found"):
            await repo.mark_success(99999)


class TestMarkFailed:
    @pytest.mark.asyncio
    async def test_updates_status(
        self, repo: SourceParseTaskRepository, parse_task: SourceParseTask
    ) -> None:
        result = await repo.mark_failed(parse_task.id, "Error message")

        assert result.status == "failed"
        assert result.error_message == "Error message"
        assert result.finished_at is not None

    @pytest.mark.asyncio
    async def test_raises_for_non_existing(
        self, repo: SourceParseTaskRepository, source: Source
    ) -> None:
        with pytest.raises(ValueError, match="Task 99999 not found"):
            await repo.mark_failed(99999, "Error")
