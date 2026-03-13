from sqlalchemy import select

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
