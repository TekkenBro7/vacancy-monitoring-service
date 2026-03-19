from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Date, cast, func, select
from sqlalchemy.exc import IntegrityError

from src.database.repositories.base_repository import BaseRepository
from src.models.sources import SourceParseTask


class SourceParseTaskRepository(BaseRepository[SourceParseTask]):
    async def get_by_id(self, task_id: int) -> SourceParseTask | None:
        return await self.session.get(SourceParseTask, task_id)

    async def get_by_source_and_date(
        self,
        source_id: int,
        parse_date: date,
    ) -> SourceParseTask | None:
        stmt = select(SourceParseTask).where(
            SourceParseTask.source_id == source_id,
            SourceParseTask.parse_date == parse_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_if_not_exists(self, source_id: int, parse_date: date) -> SourceParseTask:
        existing = await self.get_by_source_and_date(source_id, parse_date)
        if existing:
            return existing

        task = SourceParseTask(
            source_id=source_id,
            parse_date=parse_date,
            status="pending",
            attempts=0,
        )
        self.session.add(task)

        try:
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except IntegrityError:
            await self.session.rollback()
            existing = await self.get_by_source_and_date(source_id, parse_date)
            if existing is None:
                raise
            return existing

    async def has_tasks_for_source(self, source_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(SourceParseTask)
            .where(SourceParseTask.source_id == source_id)
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def get_existing_dates_for_source(
        self,
        source_id: int,
        start_date: date,
        end_date: date,
    ) -> set[date]:
        stmt = select(cast(SourceParseTask.parse_date, Date)).where(
            SourceParseTask.source_id == source_id,
            cast(SourceParseTask.parse_date, Date) >= start_date,
            cast(SourceParseTask.parse_date, Date) <= end_date,
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def get_missing_dates_for_source(
        self,
        source_id: int,
        start_date: date,
        end_date: date,
    ) -> list[date]:
        if start_date > end_date:
            return []

        has_tasks = await self.has_tasks_for_source(source_id)

        all_dates: list[date] = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)

        if not has_tasks:
            return all_dates

        existing_dates = await self.get_existing_dates_for_source(
            source_id=source_id,
            start_date=start_date,
            end_date=end_date,
        )

        return [dt for dt in all_dates if dt not in existing_dates]

    async def get_pending_tasks(self, limit: int = 100) -> list[SourceParseTask]:
        stmt = (
            select(SourceParseTask)
            .where(SourceParseTask.status == "pending")
            .order_by(SourceParseTask.parse_date.asc(), SourceParseTask.id.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_in_progress(self, task_id: int) -> SourceParseTask:
        task = await self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        task.status = "in_progress"
        task.attempts += 1
        task.started_at = datetime.now(UTC)
        task.finished_at = None
        task.error_message = None

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_tasks_for_dispatch(self, limit: int = 100) -> list[SourceParseTask]:
        stmt = (
            select(SourceParseTask)
            .where(SourceParseTask.status.in_(["pending", "failed"]))
            .order_by(SourceParseTask.parse_date.asc(), SourceParseTask.id.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_success(self, task_id: int) -> SourceParseTask:
        task = await self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        task.status = "success"
        task.finished_at = datetime.now(UTC)
        task.error_message = None

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def mark_failed(self, task_id: int, error_message: str) -> SourceParseTask:
        task = await self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        task.status = "failed"
        task.finished_at = datetime.now(UTC)
        task.error_message = error_message[:4000]

        await self.session.commit()
        await self.session.refresh(task)
        return task
