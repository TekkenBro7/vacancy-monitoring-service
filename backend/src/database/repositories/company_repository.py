from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.companies import Company


class CompanyRepository(BaseRepository[Company]):
    async def get_by_name(self, name: str) -> Company | None:
        query = select(Company).where(Company.name == name)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
