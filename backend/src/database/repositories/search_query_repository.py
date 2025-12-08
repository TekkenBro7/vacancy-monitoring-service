from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.search import SearchQuery


class SearchQueryRepository(BaseRepository[SearchQuery]):
    async def get_by_user_id(self, user_id: int) -> list[SearchQuery]:
        stmt = select(SearchQuery).where(SearchQuery.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
