from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.comparison_repository import ComparisonRepository
from src.models.comparisons import Comparison
from src.schemas.comparisons import ComparisonCreate, ComparisonRead, ComparisonUpdate


class ComparisonService:
    def __init__(self, db: AsyncSession):
        self.repo = ComparisonRepository(Comparison, db)

    async def list_comparisons(self, user_id: int) -> list[ComparisonRead]:
        items = await self.repo.get_by_user_id(user_id)
        return [
            ComparisonRead(
                id=c.id,
                name=c.name,
                user_id=c.user_id,
                vacancies=[v.id for v in c.vacancies],
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in items
        ]

    async def get_comparison(self, comp_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")
        return ComparisonRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancies=[v.id for v in comp.vacancies],
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )

    async def create_comparison(self, data: ComparisonCreate) -> ComparisonRead:
        comp = Comparison(name=data.name, user_id=data.user_id)
        try:
            comp = await self.repo.create(comp)
            return ComparisonRead(
                id=comp.id,
                name=comp.name,
                user_id=comp.user_id,
                vacancies=[],
                created_at=comp.created_at,
                updated_at=comp.updated_at,
            )
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Comparison create conflict") from e

    async def update_comparison(self, comp_id: int, data: ComparisonUpdate) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if data.name is not None:
            comp.name = data.name

        updated = await self.repo.update(comp)
        return ComparisonRead.model_validate(updated)

    async def delete_comparison(self, comp_id: int) -> dict[str, int | bool]:
        deleted = await self.repo.delete_by_id(comp_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")
        return {"deleted": True, "comparison_id": comp_id}

    async def add_vacancy(self, comp_id: int, vacancy_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        vacancy = await self.repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        comp = await self.repo.add_vacancy(comp, vacancy)

        return ComparisonRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancies=[v.id for v in comp.vacancies],
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )

    async def remove_vacancy(self, comp_id: int, vacancy_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        vacancy = await self.repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        comp = await self.repo.remove_vacancy(comp, vacancy)

        return ComparisonRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancies=[v.id for v in comp.vacancies],
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )
