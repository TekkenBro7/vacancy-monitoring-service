from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.bookmarks import Bookmark


class BookmarkRepository(BaseRepository[Bookmark]):
    async def get_by_user_id(self, user_id: int) -> list[Bookmark]:
        stmt = select(Bookmark).where(Bookmark.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
