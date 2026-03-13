from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.locations import City


class CityRepository(BaseRepository[City]):
    async def get_by_name(self, name: str) -> City | None:
        query = select(City).where(City.name == name)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
