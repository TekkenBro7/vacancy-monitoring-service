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


class VacancyService:
    def __init__(self, db: AsyncSession):
        self.repo = VacancyRepository(Vacancy, db)
        self.enrichment_service = VacancyEnrichmentService(db)

    async def list_vacancies(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[VacancyRead]:
        offset = (page - 1) * page_size
        items = await self.repo.list_with_related(limit=page_size, offset=offset)
        total_items = await self.repo.count()
        total_pages = (total_items + page_size - 1) // page_size

        return PaginatedResponse(
            items=[VacancyRead.model_validate(obj) for obj in items],
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )

    async def get_vacancy(self, vacancy_id: int) -> VacancyRead:
        vacancy = await self.repo.get_by_id_with_related(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        vacancy = await self.enrichment_service.enrich_vacancy_if_needed(vacancy)

        if vacancy.last_enriched_at:
            vacancy = await self.repo.update(vacancy)

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
        vacancy = await self.repo.get_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            if isinstance(value, HttpUrl):
                value = str(value)
            setattr(vacancy, key, value)

        try:
            updated = await self.repo.update(vacancy)
            return VacancyRead.model_validate(updated)

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
