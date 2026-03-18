from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.sources import Source


class SourceRepository(BaseRepository[Source]):
    async def get_by_name(self, name: str) -> Source | None:
        query = select(Source).where(Source.name == name)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
