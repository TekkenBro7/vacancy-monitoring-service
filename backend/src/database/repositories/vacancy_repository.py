from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.companies import Company, Vacancy
from src.models.currencies import Currency
from src.models.locations import City
from src.models.secondary_tables import vacancy_skills_table
from src.models.skills import Skill
from src.models.sources import Source
from src.schemas.vacancies import SalaryRange, SortOrder, VacancyFilters, VacancySortField


class VacancyRepository(BaseRepository[Vacancy]):
    async def get_by_source_and_external_id(
        self, source_id: int, external_id: str
    ) -> Vacancy | None:
        query = select(Vacancy).where(
            Vacancy.source_id == source_id, Vacancy.external_id == external_id
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_fingerprint(self, fingerprint: str) -> Vacancy | None:
        query = select(Vacancy).where(Vacancy.fingerprint == fingerprint)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_with_related(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Vacancy]:
        query = (
            select(Vacancy)
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.location),
                selectinload(Vacancy.currency),
                selectinload(Vacancy.source),
                selectinload(Vacancy.skills),
            )
            .order_by(Vacancy.published_at.desc().nulls_last(), Vacancy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_with_related(self, vacancy_id: int) -> Vacancy | None:
        query = (
            select(Vacancy)
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.location),
                selectinload(Vacancy.currency),
                selectinload(Vacancy.source),
                selectinload(Vacancy.skills),
            )
            .where(Vacancy.id == vacancy_id)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count(self) -> int:
        query = select(func.count()).select_from(Vacancy)
        result = await self.session.execute(query)
        return result.scalar_one()

    def _apply_filters(
        self, query: Select[tuple[Any, ...]], filters: VacancyFilters
    ) -> Select[tuple[Any, ...]]:
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.where(
                or_(
                    func.lower(Vacancy.title).like(search_term),
                    func.lower(Vacancy.description).like(search_term),
                )
            )

        if filters.source_ids:
            query = query.where(Vacancy.source_id.in_(filters.source_ids))

        if filters.company_ids:
            query = query.where(Vacancy.company_id.in_(filters.company_ids))

        if filters.city_ids:
            query = query.where(Vacancy.location_id.in_(filters.city_ids))

        if filters.is_remote is not None:
            query = query.where(Vacancy.is_remote == filters.is_remote)

        if filters.salary_range and filters.salary_range != SalaryRange.ANY:
            query = self._apply_salary_range(query, filters.salary_range)
        else:
            if filters.salary_from is not None:
                query = query.where(
                    or_(
                        Vacancy.salary_from >= filters.salary_from,
                        Vacancy.salary_to >= filters.salary_from,
                    )
                )
            if filters.salary_to is not None:
                query = query.where(
                    or_(
                        Vacancy.salary_from <= filters.salary_to,
                        Vacancy.salary_to <= filters.salary_to,
                    )
                )

        if filters.with_salary_only:
            query = query.where(
                or_(
                    Vacancy.salary_from.is_not(None),
                    Vacancy.salary_to.is_not(None),
                )
            )

        if filters.currency_id:
            query = query.where(Vacancy.currency_id == filters.currency_id)

        if filters.experience:
            query = query.where(Vacancy.experience.in_(filters.experience))

        if filters.employment:
            query = query.where(Vacancy.employment.in_(filters.employment))

        if filters.schedule:
            query = query.where(Vacancy.schedule.in_(filters.schedule))

        if filters.internship is not None:
            query = query.where(Vacancy.internship == filters.internship)

        if filters.is_active is not None:
            query = query.where(Vacancy.is_active == filters.is_active)

        if filters.published_after:
            query = query.where(Vacancy.published_at >= filters.published_after)
        if filters.published_before:
            query = query.where(Vacancy.published_at <= filters.published_before)

        if filters.skill_ids:
            for skill_id in filters.skill_ids:
                subquery = select(vacancy_skills_table.c.vacancy_id).where(
                    vacancy_skills_table.c.skill_id == skill_id
                )
                query = query.where(Vacancy.id.in_(subquery))

        return query

    def _apply_salary_range(
        self, query: Select[tuple[Any, ...]], salary_range: SalaryRange
    ) -> Select[tuple[Any, ...]]:
        ranges: dict[SalaryRange, tuple[int | None, int | None]] = {
            SalaryRange.UP_TO_50K: (None, 50000),
            SalaryRange.FROM_50K_TO_100K: (50000, 100000),
            SalaryRange.FROM_100K_TO_150K: (100000, 150000),
            SalaryRange.FROM_150K_TO_200K: (150000, 200000),
            SalaryRange.FROM_200K: (200000, None),
        }

        min_salary, max_salary = ranges.get(salary_range, (None, None))

        if min_salary is not None:
            query = query.where(
                or_(
                    Vacancy.salary_from >= min_salary,
                    Vacancy.salary_to >= min_salary,
                )
            )
        if max_salary is not None:
            query = query.where(
                or_(
                    Vacancy.salary_from <= max_salary,
                    Vacancy.salary_to <= max_salary,
                    and_(
                        Vacancy.salary_from.is_(None),
                        Vacancy.salary_to <= max_salary,
                    ),
                )
            )

        return query

    def _apply_sorting(
        self,
        query: Select[tuple[Any, ...]],
        sort_by: VacancySortField,
        sort_order: SortOrder,
    ) -> Select[tuple[Any, ...]]:
        sort_columns = {
            VacancySortField.PUBLISHED_AT: Vacancy.published_at,
            VacancySortField.SALARY_FROM: Vacancy.salary_from,
            VacancySortField.SALARY_TO: Vacancy.salary_to,
            VacancySortField.TITLE: Vacancy.title,
            VacancySortField.CREATED_AT: Vacancy.created_at,
        }

        column = sort_columns.get(sort_by, Vacancy.published_at)

        if sort_order == SortOrder.DESC:
            query = query.order_by(column.desc().nulls_last())
        else:
            query = query.order_by(column.asc().nulls_last())

        query = query.order_by(Vacancy.id.desc())

        return query

    async def search_with_filters(
        self,
        filters: VacancyFilters,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Vacancy]:
        query = select(Vacancy).options(
            selectinload(Vacancy.company),
            selectinload(Vacancy.location),
            selectinload(Vacancy.currency),
            selectinload(Vacancy.source),
            selectinload(Vacancy.skills),
        )

        query = self._apply_filters(query, filters)
        query = self._apply_sorting(query, filters.sort_by, filters.sort_order)
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_with_filters(self, filters: VacancyFilters) -> int:
        query = select(func.count()).select_from(Vacancy)
        query = self._apply_filters(query, filters)

        result = await self.session.execute(query)
        return result.scalar_one()

    def _create_filter_without_field(
        self, filters: VacancyFilters, exclude_field: str
    ) -> VacancyFilters:
        filter_dict = filters.model_dump()
        filter_dict.pop(exclude_field, None)
        return VacancyFilters(**filter_dict)

    def _create_filter_without_fields(
        self, filters: VacancyFilters, exclude_fields: list[str]
    ) -> VacancyFilters:
        filter_dict = filters.model_dump()
        for field in exclude_fields:
            filter_dict.pop(field, None)
        return VacancyFilters(**filter_dict)

    async def get_filter_options_dynamic(self, filters: VacancyFilters) -> dict[str, Any]:
        results: dict[str, Any] = {}

        source_filters = self._create_filter_without_field(filters, "source_ids")
        source_base_query = self._apply_filters(select(Vacancy.id), source_filters)

        sources_query = (
            select(
                Source.id,
                Source.name,
                func.count(Vacancy.id).label("count"),
            )
            .join(Vacancy, Vacancy.source_id == Source.id)
            .where(Vacancy.id.in_(source_base_query.scalar_subquery()))
            .group_by(Source.id, Source.name)
            .order_by(func.count(Vacancy.id).desc())
        )
        sources_result = await self.session.execute(sources_query)
        results["sources"] = [
            {"id": row.id, "name": row.name, "count": row.count} for row in sources_result
        ]

        company_filters = self._create_filter_without_field(filters, "company_ids")
        company_base_query = self._apply_filters(select(Vacancy.id), company_filters)

        companies_query = (
            select(
                Company.id,
                Company.name,
                func.count(Vacancy.id).label("count"),
            )
            .join(Vacancy, Vacancy.company_id == Company.id)
            .where(Vacancy.id.in_(company_base_query.scalar_subquery()))
            .group_by(Company.id, Company.name)
            .order_by(func.count(Vacancy.id).desc())
            .limit(100)
        )
        companies_result = await self.session.execute(companies_query)
        results["companies"] = [
            {"id": row.id, "name": row.name, "count": row.count} for row in companies_result
        ]

        city_filters = self._create_filter_without_field(filters, "city_ids")
        city_base_query = self._apply_filters(select(Vacancy.id), city_filters)

        cities_query = (
            select(
                City.id,
                City.name,
                func.count(Vacancy.id).label("count"),
            )
            .join(Vacancy, Vacancy.location_id == City.id)
            .where(Vacancy.id.in_(city_base_query.scalar_subquery()))
            .group_by(City.id, City.name)
            .order_by(func.count(Vacancy.id).desc())
            .limit(100)
        )
        cities_result = await self.session.execute(cities_query)
        results["cities"] = [
            {"id": row.id, "name": row.name, "count": row.count} for row in cities_result
        ]

        currency_filters = self._create_filter_without_field(filters, "currency_id")
        currency_base_query = self._apply_filters(select(Vacancy.id), currency_filters)

        currencies_query = (
            select(
                Currency.id,
                Currency.name,
                func.count(Vacancy.id).label("count"),
            )
            .join(Vacancy, Vacancy.currency_id == Currency.id)
            .where(Vacancy.id.in_(currency_base_query.scalar_subquery()))
            .group_by(Currency.id, Currency.name)
            .order_by(func.count(Vacancy.id).desc())
        )
        currencies_result = await self.session.execute(currencies_query)
        results["currencies"] = [
            {"id": row.id, "name": row.name, "count": row.count} for row in currencies_result
        ]

        skill_filters = self._create_filter_without_fields(filters, ["skill_ids"])
        skill_base_query = self._apply_filters(select(Vacancy.id), skill_filters)

        skills_query = (
            select(
                Skill.id,
                Skill.name,
                func.count(vacancy_skills_table.c.vacancy_id.distinct()).label("count"),
            )
            .join(vacancy_skills_table, vacancy_skills_table.c.skill_id == Skill.id)
            .where(vacancy_skills_table.c.vacancy_id.in_(skill_base_query.scalar_subquery()))
            .group_by(Skill.id, Skill.name)
            .order_by(func.count(vacancy_skills_table.c.vacancy_id.distinct()).desc())
            .limit(50)
        )
        skills_result = await self.session.execute(skills_query)
        results["skills"] = [
            {"id": row.id, "name": row.name, "count": row.count} for row in skills_result
        ]

        experience_filters = self._create_filter_without_field(filters, "experience")
        experience_base_query = self._apply_filters(select(Vacancy.id), experience_filters)

        experience_query = (
            select(
                Vacancy.experience,
                func.count(Vacancy.id).label("count"),
            )
            .where(Vacancy.experience.is_not(None))
            .where(Vacancy.id.in_(experience_base_query.scalar_subquery()))
            .group_by(Vacancy.experience)
            .order_by(func.count(Vacancy.id).desc())
        )
        experience_result = await self.session.execute(experience_query)
        results["experience"] = [
            {"id": row.experience, "name": row.experience, "count": row.count}
            for row in experience_result
        ]

        employment_filters = self._create_filter_without_field(filters, "employment")
        employment_base_query = self._apply_filters(select(Vacancy.id), employment_filters)

        employment_query = (
            select(
                Vacancy.employment,
                func.count(Vacancy.id).label("count"),
            )
            .where(Vacancy.employment.is_not(None))
            .where(Vacancy.id.in_(employment_base_query.scalar_subquery()))
            .group_by(Vacancy.employment)
            .order_by(func.count(Vacancy.id).desc())
        )
        employment_result = await self.session.execute(employment_query)
        results["employment"] = [
            {"id": row.employment, "name": row.employment, "count": row.count}
            for row in employment_result
        ]

        schedule_filters = self._create_filter_without_field(filters, "schedule")
        schedule_base_query = self._apply_filters(select(Vacancy.id), schedule_filters)

        schedule_query = (
            select(
                Vacancy.schedule,
                func.count(Vacancy.id).label("count"),
            )
            .where(Vacancy.schedule.is_not(None))
            .where(Vacancy.id.in_(schedule_base_query.scalar_subquery()))
            .group_by(Vacancy.schedule)
            .order_by(func.count(Vacancy.id).desc())
        )
        schedule_result = await self.session.execute(schedule_query)
        results["schedule"] = [
            {"id": row.schedule, "name": row.schedule, "count": row.count}
            for row in schedule_result
        ]

        full_base_query = self._apply_filters(select(Vacancy.id), filters)

        remote_filters = self._create_filter_without_field(filters, "is_remote")
        remote_base = self._apply_filters(select(Vacancy.id), remote_filters)
        remote_query = (
            select(func.count())
            .select_from(Vacancy)
            .where(Vacancy.id.in_(remote_base.scalar_subquery()))
            .where(Vacancy.is_remote == True)  # noqa: E712
        )
        remote_result = await self.session.execute(remote_query)
        results["remote_count"] = remote_result.scalar_one()

        salary_filters = self._create_filter_without_field(filters, "with_salary_only")
        salary_base = self._apply_filters(select(Vacancy.id), salary_filters)
        salary_query = (
            select(func.count())
            .select_from(Vacancy)
            .where(Vacancy.id.in_(salary_base.scalar_subquery()))
            .where(
                or_(
                    Vacancy.salary_from.is_not(None),
                    Vacancy.salary_to.is_not(None),
                )
            )
        )
        salary_result = await self.session.execute(salary_query)
        results["with_salary_count"] = salary_result.scalar_one()

        internship_filters = self._create_filter_without_field(filters, "internship")
        internship_base = self._apply_filters(select(Vacancy.id), internship_filters)
        internship_query = (
            select(func.count())
            .select_from(Vacancy)
            .where(Vacancy.id.in_(internship_base.scalar_subquery()))
            .where(Vacancy.internship == True)  # noqa: E712
        )
        internship_result = await self.session.execute(internship_query)
        results["internship_count"] = internship_result.scalar_one()

        total_query = (
            select(func.count())
            .select_from(Vacancy)
            .where(Vacancy.id.in_(full_base_query.scalar_subquery()))
        )
        total_result = await self.session.execute(total_query)
        results["total_vacancies"] = total_result.scalar_one()

        return results

    async def search_filter_options(
        self,
        filter_type: str,
        query: str,
        limit: int = 50,
        base_filters: VacancyFilters | None = None,
    ) -> list[dict[str, Any]]:
        base_query = select(Vacancy.id)
        if base_filters:
            base_query = self._apply_filters(base_query, base_filters)
        base_ids_subquery = base_query.scalar_subquery()

        if filter_type == "companies":
            search_query = select(
                Company.id,
                Company.name,
                func.count(Vacancy.id).label("count"),
            ).join(Vacancy, Vacancy.company_id == Company.id)

            if base_filters:
                search_query = search_query.where(Vacancy.id.in_(base_ids_subquery))

            if query.strip():
                search_query = search_query.where(
                    func.lower(Company.name).contains(query.lower().strip())
                )

            search_query = (
                search_query.group_by(Company.id, Company.name)
                .order_by(func.count(Vacancy.id).desc())
                .limit(limit)
            )

        elif filter_type == "cities":
            search_query = select(
                City.id,
                City.name,
                func.count(Vacancy.id).label("count"),
            ).join(Vacancy, Vacancy.location_id == City.id)

            if base_filters:
                search_query = search_query.where(Vacancy.id.in_(base_ids_subquery))

            if query.strip():
                search_query = search_query.where(
                    func.lower(City.name).contains(query.lower().strip())
                )

            search_query = (
                search_query.group_by(City.id, City.name)
                .order_by(func.count(Vacancy.id).desc())
                .limit(limit)
            )

        elif filter_type == "skills":
            search_query = select(
                Skill.id,
                Skill.name,
                func.count(vacancy_skills_table.c.vacancy_id.distinct()).label("count"),
            ).join(vacancy_skills_table, vacancy_skills_table.c.skill_id == Skill.id)

            if base_filters:
                search_query = search_query.where(
                    vacancy_skills_table.c.vacancy_id.in_(base_ids_subquery)
                )

            if query.strip():
                search_query = search_query.where(
                    func.lower(Skill.name).contains(query.lower().strip())
                )

            search_query = (
                search_query.group_by(Skill.id, Skill.name)
                .order_by(func.count(vacancy_skills_table.c.vacancy_id.distinct()).desc())
                .limit(limit)
            )
        else:
            return []

        result = await self.session.execute(search_query)
        return [{"id": row.id, "name": row.name, "count": row.count} for row in result]
