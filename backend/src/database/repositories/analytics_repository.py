from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Date,
    Float,
    Row,
    and_,
    case,
    cast,
    desc,
    distinct,
    extract,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bookmarks import Bookmark
from src.models.comments import Comment
from src.models.companies import Company, Vacancy
from src.models.locations import City
from src.models.secondary_tables import user_skills_table, vacancy_skills_table
from src.models.skills import Skill
from src.models.sources import Source, SourceParseTask, SourceType
from src.models.users import Role, User


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_vacancy_counts(self) -> dict[str, int]:
        query = select(
            func.count(Vacancy.id).label("total"),
            func.count(case((Vacancy.is_active == True, 1))).label("active"),  # noqa: E712
            func.count(
                case((or_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)), 1))
            ).label("with_salary"),
            func.count(case((Vacancy.is_remote == True, 1))).label("remote"),  # noqa: E712
            func.count(case((Vacancy.internship == True, 1))).label("internship"),  # noqa: E712
        )
        result = await self.session.execute(query)
        row = result.one()
        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "with_salary": row.with_salary or 0,
            "remote": row.remote or 0,
            "internship": row.internship or 0,
        }

    async def count_users(self) -> int:
        result = await self.session.scalar(select(func.count(User.id)))
        return result or 0

    async def count_companies(self) -> int:
        result = await self.session.scalar(select(func.count(Company.id)))
        return result or 0

    async def count_skills(self) -> int:
        result = await self.session.scalar(select(func.count(Skill.id)))
        return result or 0

    async def count_sources(self) -> int:
        result = await self.session.scalar(select(func.count(Source.id)))
        return result or 0

    async def count_bookmarks(self) -> int:
        result = await self.session.scalar(select(func.count(Bookmark.id)))
        return result or 0

    async def count_comments(self) -> int:
        result = await self.session.scalar(select(func.count(Comment.id)))
        return result or 0

    async def count_vacancies_in_period(self, start: datetime, end: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(
                and_(Vacancy.created_at >= start, Vacancy.created_at < end)
            )
        )
        return result or 0

    async def count_users_in_period(self, start: datetime, end: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(User.id)).where(and_(User.created_at >= start, User.created_at < end))
        )
        return result or 0

    async def count_companies_in_period(self, start: datetime, end: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(Company.id)).where(
                and_(Company.created_at >= start, Company.created_at < end)
            )
        )
        return result or 0

    async def count_bookmarks_in_period(self, start: datetime, end: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(Bookmark.id)).where(
                and_(Bookmark.created_at >= start, Bookmark.created_at < end)
            )
        )
        return result or 0

    async def get_vacancies_by_date(self, start_date: datetime) -> list[tuple[Any, int]]:
        query = (
            select(
                cast(Vacancy.created_at, Date).label("date"),
                func.count(Vacancy.id).label("cnt"),
            )
            .where(Vacancy.created_at >= start_date)
            .group_by(cast(Vacancy.created_at, Date))
            .order_by(cast(Vacancy.created_at, Date))
        )
        result = await self.session.execute(query)
        return [(row.date, row.cnt) for row in result.all()]

    async def get_salaries(
        self, currency_id: int | None = None
    ) -> list[tuple[int | None, int | None]]:
        salary_filter = or_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None))
        if currency_id:
            salary_filter = and_(salary_filter, Vacancy.currency_id == currency_id)

        query = select(Vacancy.salary_from, Vacancy.salary_to).where(salary_filter)
        result = await self.session.execute(query)
        return [(row.salary_from, row.salary_to) for row in result.all()]

    async def count_vacancies_without_salary(self) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(
                and_(Vacancy.salary_from.is_(None), Vacancy.salary_to.is_(None))
            )
        )
        return result or 0

    async def get_top_companies_raw(self, limit: int = 10) -> Sequence[Row[Any]]:
        query = (
            select(
                Company.id,
                Company.name,
                func.count(Vacancy.id).label("vacancy_count"),
                func.avg(
                    case(
                        (
                            and_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)),
                            (Vacancy.salary_from + Vacancy.salary_to) / 2,
                        ),
                        (Vacancy.salary_from.isnot(None), cast(Vacancy.salary_from, Float)),
                        (Vacancy.salary_to.isnot(None), cast(Vacancy.salary_to, Float)),
                    )
                ).label("avg_salary"),
                func.bool_or(Vacancy.is_remote).label("has_remote"),
            )
            .join(Vacancy, Company.id == Vacancy.company_id)
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Company.id, Company.name)
            .order_by(desc("vacancy_count"))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_active_vacancies_count(self) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(Vacancy.is_active == True)  # noqa: E712
        )
        return result or 1

    async def get_top_skills_raw(self, limit: int = 20) -> Sequence[Row[Any]]:
        query = (
            select(
                Skill.id,
                Skill.name,
                func.count(distinct(vacancy_skills_table.c.vacancy_id)).label("vacancy_count"),
            )
            .join(vacancy_skills_table, Skill.id == vacancy_skills_table.c.skill_id)
            .join(Vacancy, vacancy_skills_table.c.vacancy_id == Vacancy.id)
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Skill.id, Skill.name)
            .order_by(desc("vacancy_count"))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_top_cities_raw(self, limit: int = 10) -> Sequence[Row[Any]]:
        query = (
            select(
                City.id,
                City.name,
                func.count(Vacancy.id).label("vacancy_count"),
                func.avg(
                    case(
                        (
                            and_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)),
                            (Vacancy.salary_from + Vacancy.salary_to) / 2,
                        ),
                        (Vacancy.salary_from.isnot(None), cast(Vacancy.salary_from, Float)),
                        (Vacancy.salary_to.isnot(None), cast(Vacancy.salary_to, Float)),
                    )
                ).label("avg_salary"),
            )
            .join(Vacancy, City.id == Vacancy.location_id)
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(City.id, City.name)
            .order_by(desc("vacancy_count"))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_total_vacancies_count(self) -> int:
        result = await self.session.scalar(select(func.count(Vacancy.id)))
        return result or 1

    async def get_sources_stats_raw(self) -> Sequence[Row[Any]]:
        query = (
            select(
                Source.id,
                Source.name,
                SourceType.type_name,
                func.count(Vacancy.id).label("vacancy_count"),
                func.count(case((Vacancy.is_active == True, 1))).label(  # noqa: E712
                    "active_count"
                ),
                func.max(Vacancy.created_at).label("last_parsed"),
                func.avg(
                    case(
                        (
                            and_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)),
                            (Vacancy.salary_from + Vacancy.salary_to) / 2,
                        ),
                        (Vacancy.salary_from.isnot(None), cast(Vacancy.salary_from, Float)),
                        (Vacancy.salary_to.isnot(None), cast(Vacancy.salary_to, Float)),
                    )
                ).label("avg_salary"),
            )
            .join(SourceType, Source.source_type_id == SourceType.id)
            .outerjoin(Vacancy, Source.id == Vacancy.source_id)
            .group_by(Source.id, Source.name, SourceType.type_name)
            .order_by(desc("vacancy_count"))
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_source_parsing_stats_raw(self, start_date: datetime) -> Sequence[Row[Any]]:
        query = (
            select(
                Source.id,
                Source.name,
                func.count(SourceParseTask.id).label("total"),
                func.count(case((SourceParseTask.status == "completed", 1))).label("success"),
                func.count(case((SourceParseTask.status == "failed", 1))).label("failed"),
                func.count(case((SourceParseTask.status == "pending", 1))).label("pending"),
                func.max(
                    case((SourceParseTask.status == "completed", SourceParseTask.finished_at))
                ).label("last_success"),
                func.max(
                    case((SourceParseTask.status == "failed", SourceParseTask.finished_at))
                ).label("last_failure"),
                func.avg(
                    case(
                        (
                            and_(
                                SourceParseTask.started_at.isnot(None),
                                SourceParseTask.finished_at.isnot(None),
                            ),
                            extract(
                                "epoch", SourceParseTask.finished_at - SourceParseTask.started_at
                            ),
                        )
                    )
                ).label("avg_duration"),
            )
            .join(SourceParseTask, Source.id == SourceParseTask.source_id)
            .where(SourceParseTask.created_at >= start_date)
            .group_by(Source.id, Source.name)
        )
        result = await self.session.execute(query)
        return result.all()

    async def count_users_since(self, since: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(User.id)).where(User.created_at >= since)
        )
        return result or 0

    async def count_users_with_bookmarks(self) -> int:
        result = await self.session.scalar(select(func.count(distinct(Bookmark.user_id))))
        return result or 0

    async def count_users_with_skills(self) -> int:
        result = await self.session.scalar(
            select(func.count(distinct(user_skills_table.c.user_id)))
        )
        return result or 0

    async def count_total_user_skills(self) -> int:
        result = await self.session.scalar(select(func.count()).select_from(user_skills_table))
        return result or 0

    async def get_users_by_date(self, start_date: datetime) -> list[tuple[Any, int]]:
        query = (
            select(
                cast(User.created_at, Date).label("date"),
                func.count(User.id).label("cnt"),
            )
            .where(User.created_at >= start_date)
            .group_by(cast(User.created_at, Date))
            .order_by(cast(User.created_at, Date))
        )
        result = await self.session.execute(query)
        return [(row.date, row.cnt) for row in result.all()]

    async def get_users_by_role_raw(self) -> Sequence[Row[Any]]:
        query = (
            select(
                Role.id,
                Role.name,
                func.count(User.id).label("cnt"),
            )
            .join(User, Role.id == User.role_id)
            .group_by(Role.id, Role.name)
            .order_by(desc("cnt"))
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_experience_stats_raw(self) -> Sequence[Row[Any]]:
        query = (
            select(
                Vacancy.experience,
                func.count(Vacancy.id).label("cnt"),
                func.avg(
                    case(
                        (
                            and_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)),
                            (Vacancy.salary_from + Vacancy.salary_to) / 2,
                        ),
                        (Vacancy.salary_from.isnot(None), cast(Vacancy.salary_from, Float)),
                        (Vacancy.salary_to.isnot(None), cast(Vacancy.salary_to, Float)),
                    )
                ).label("avg_salary"),
            )
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Vacancy.experience)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_employment_stats_raw(self) -> Sequence[Row[Any]]:
        query = (
            select(
                Vacancy.employment,
                func.count(Vacancy.id).label("cnt"),
            )
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Vacancy.employment)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_schedule_stats_raw(self) -> Sequence[Row[Any]]:
        query = (
            select(
                Vacancy.schedule,
                func.count(Vacancy.id).label("cnt"),
            )
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Vacancy.schedule)
        )
        result = await self.session.execute(query)
        return result.all()

    async def count_remote_active_vacancies(self) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(
                and_(
                    Vacancy.is_active == True,  # noqa: E712
                    Vacancy.is_remote == True,  # noqa: E712
                )
            )
        )
        return result or 0

    async def count_internship_active_vacancies(self) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(
                and_(
                    Vacancy.is_active == True,  # noqa: E712
                    Vacancy.internship == True,  # noqa: E712
                )
            )
        )
        return result or 0

    async def count_active_vacancies_with_salary(self) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(
                and_(
                    Vacancy.is_active == True,  # noqa: E712
                    or_(Vacancy.salary_from.isnot(None), Vacancy.salary_to.isnot(None)),
                )
            )
        )
        return result or 0

    async def count_vacancies_since(self, since: datetime) -> int:
        result = await self.session.scalar(
            select(func.count(Vacancy.id)).where(Vacancy.created_at >= since)
        )
        return result or 0
