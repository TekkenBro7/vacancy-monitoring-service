from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.bookmarks import Bookmark
from src.models.companies import Vacancy


class BookmarkRepository(BaseRepository[Bookmark]):
    async def get_by_user_id(self, user_id: int) -> list[Bookmark]:
        query = (
            select(Bookmark)
            .where(Bookmark.user_id == user_id)
            .options(
                selectinload(Bookmark.vacancy).selectinload(Vacancy.company),
                selectinload(Bookmark.vacancy).selectinload(Vacancy.location),
                selectinload(Bookmark.vacancy).selectinload(Vacancy.currency),
                selectinload(Bookmark.vacancy).selectinload(Vacancy.source),
                selectinload(Bookmark.vacancy).selectinload(Vacancy.skills),
            )
            .order_by(Bookmark.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_vacancy(self, user_id: int, vacancy_id: int) -> Bookmark | None:
        query = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.vacancy_id == vacancy_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_bookmark_ids(self, user_id: int) -> list[int]:
        query = select(Bookmark.vacancy_id).where(Bookmark.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_by_user_and_vacancy(self, user_id: int, vacancy_id: int) -> bool:
        bookmark = await self.get_by_user_and_vacancy(user_id, vacancy_id)
        if bookmark:
            await self.session.delete(bookmark)
            await self.session.commit()
            return True
        return False
