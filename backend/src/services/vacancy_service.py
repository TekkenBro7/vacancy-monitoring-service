from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Vacancy
from src.parsers.hh_ru.vacancy_enrichment_service import VacancyEnrichmentService
from src.schemas.companies import (
    PaginatedResponse,
    PaginationInfo,
    VacancyCreate,
    VacancyRead,
    VacancyUpdate,
)
from src.schemas.vacancies import (
    AvailableFilters,
    FilterOption,
    VacancyFilters,
    VacancySearchResponse,
)


class VacancyService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = VacancyRepository(Vacancy, db)
        self.enrichment_service = VacancyEnrichmentService(db)

    async def search_vacancies(
        self,
        filters: VacancyFilters,
        page: int = 1,
        page_size: int = 20,
        include_filters: bool = False,
    ) -> VacancySearchResponse:
        offset = (page - 1) * page_size

        items = await self.repo.search_with_filters(
            filters=filters,
            limit=page_size,
            offset=offset,
        )

        total_items = await self.repo.count_with_filters(filters)
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

        available_filters: AvailableFilters | None = None
        if include_filters:
            filter_options = await self.repo.get_filter_options_dynamic(filters)
            available_filters = AvailableFilters(
                sources=[FilterOption(**s) for s in filter_options["sources"]],
                companies=[FilterOption(**c) for c in filter_options["companies"]],
                cities=[FilterOption(**c) for c in filter_options["cities"]],
                currencies=[FilterOption(**c) for c in filter_options["currencies"]],
                skills=[FilterOption(**s) for s in filter_options["skills"]],
                experience=[FilterOption(**e) for e in filter_options["experience"]],
                employment=[FilterOption(**e) for e in filter_options["employment"]],
                schedule=[FilterOption(**s) for s in filter_options["schedule"]],
                total_vacancies=filter_options["total_vacancies"],
                with_salary_count=filter_options["with_salary_count"],
                remote_count=filter_options["remote_count"],
                internship_count=filter_options["internship_count"],
            )

        return VacancySearchResponse(
            items=[VacancyRead.model_validate(v) for v in items],
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
            filters=available_filters,
        )

    async def search_filter_options(
        self,
        filter_type: str,
        query: str,
        limit: int = 50,
        base_filters: VacancyFilters | None = None,
    ) -> list[FilterOption]:
        options = await self.repo.search_filter_options(
            filter_type=filter_type,
            query=query,
            limit=limit,
            base_filters=base_filters,
        )
        return [FilterOption(**opt) for opt in options]

    async def list_vacancies(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[VacancyRead]:
        result = await self.search_vacancies(
            filters=VacancyFilters(),
            page=page,
            page_size=page_size,
        )
        
        return PaginatedResponse(
            items=result.items,
            pagination=result.pagination,
        )

    async def get_vacancy(self, vacancy_id: int) -> VacancyRead:
        vacancy = await self.repo.get_by_id_with_related(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        vacancy = await self.enrichment_service.enrich_vacancy_if_needed(vacancy)

        if vacancy.last_enriched_at:
            await self.repo.update(vacancy)
            vacancy = await self.repo.get_by_id_with_related(vacancy_id)

        return VacancyRead.model_validate(vacancy)

    async def create_vacancy(self, data: VacancyCreate) -> VacancyRead:
        try:
            vacancy_model = Vacancy(
                title=data.title,
                description=data.description,
                salary_from=data.salary_from,
                salary_to=data.salary_to,
                currency_id=data.currency_id,
                company_id=data.company_id,
                source_id=data.source_id,
                location_id=data.location_id,
                vacancy_url=str(data.vacancy_url) if data.vacancy_url else None,
                is_remote=data.is_remote,
                is_active=data.is_active,
                published_at=data.published_at,
            )

            vacancy = await self.repo.create(vacancy_model)
            return VacancyRead.model_validate(vacancy)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Vacancy create conflict",
            ) from e

    async def update_vacancy(self, vacancy_id: int, data: VacancyUpdate) -> VacancyRead:
        vacancy = await self.repo.get_by_id_with_related(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        update_data = data.model_dump(exclude_unset=True)

        skill_ids = update_data.pop("skill_ids", None)

        for key, value in update_data.items():
            if isinstance(value, HttpUrl):
                value = str(value)
            setattr(vacancy, key, value)

        if skill_ids is not None:
            await self.repo.update_vacancy_skills(vacancy, skill_ids)

        try:
            await self.repo.update(vacancy)
            updated_with_related = await self.repo.get_by_id_with_related(vacancy_id)
            return VacancyRead.model_validate(updated_with_related)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Vacancy update conflict",
            ) from e

    async def delete_vacancy(self, vacancy_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(vacancy_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        return {"deleted": True, "vacancy_id": vacancy_id}
