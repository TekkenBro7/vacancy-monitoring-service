from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.companies import Vacancy


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
        """Получить список вакансий с загруженными связанными данными и пагинацией"""
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
