from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Vacancy
from src.schemas.companies import VacancyCreate, VacancyRead, VacancyUpdate


class VacancyService:
    def __init__(self, db: AsyncSession):
        self.repo = VacancyRepository(Vacancy, db)

    async def list_vacancies(self) -> list[VacancyRead]:
        items = await self.repo.list()
        return [VacancyRead.model_validate(obj) for obj in items]

    async def get_vacancy(self, vacancy_id: int) -> VacancyRead:
        vacancy = await self.repo.get_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")
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
