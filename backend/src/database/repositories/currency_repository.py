from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.currencies import Currency


class CurrencyRepository(BaseRepository[Currency]):
    async def get_by_code(self, code: str) -> Currency | None:
        query = select(Currency).where(Currency.name == code)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
