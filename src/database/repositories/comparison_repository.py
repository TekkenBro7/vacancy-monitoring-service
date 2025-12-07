from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.companies import Vacancy
from src.models.comparisons import Comparison


class ComparisonRepository(BaseRepository[Comparison]):
    async def get_by_user_id(self, user_id: int) -> list[Comparison]:
        stmt = (
            select(Comparison)
            .where(Comparison.user_id == user_id)
            .options(selectinload(Comparison.vacancies))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, comp_id: int) -> Comparison | None:
        stmt = (
            select(Comparison)
            .where(Comparison.id == comp_id)
            .options(selectinload(Comparison.vacancies))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vacancy_by_id(self, vacancy_id: int) -> Vacancy | None:
        return await self.session.get(Vacancy, vacancy_id)

    async def add_vacancy(self, comp: Comparison, vacancy: Vacancy) -> Comparison:
        if vacancy not in comp.vacancies:
            comp.vacancies.append(vacancy)
            await self.session.commit()
            await self.session.refresh(comp)
        return comp

    async def remove_vacancy(self, comp: Comparison, vacancy: Vacancy) -> Comparison:
        if vacancy in comp.vacancies:
            comp.vacancies.remove(vacancy)
            await self.session.commit()
            await self.session.refresh(comp)
        return comp
