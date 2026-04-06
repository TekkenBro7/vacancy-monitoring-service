from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.bookmark_repository import BookmarkRepository
from src.models.bookmarks import Bookmark
from src.schemas.bookmarks import BookmarkCreate, BookmarkRead


class BookmarkService:
    def __init__(self, db: AsyncSession):
        self.repo = BookmarkRepository(Bookmark, db)

    async def create_bookmark(self, data: BookmarkCreate) -> BookmarkRead:
        try:
            existing = await self.repo.get_by_user_and_vacancy(data.user_id, data.vacancy_id)
            if existing:
                raise HTTPException(status.HTTP_409_CONFLICT, "Bookmark already exists")

            bookmark_model = Bookmark(
                user_id=data.user_id,
                vacancy_id=data.vacancy_id,
            )

            bookmark = await self.repo.create(bookmark_model)
            bookmarks = await self.repo.get_by_user_id(data.user_id)
            for b in bookmarks:
                if b.id == bookmark.id:
                    return BookmarkRead.model_validate(b)
            return BookmarkRead.model_validate(bookmark)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Bookmark create conflict") from e

    async def list_user_bookmarks(self, user_id: int) -> list[BookmarkRead]:
        items = await self.repo.get_by_user_id(user_id)
        return [BookmarkRead.model_validate(i) for i in items]

    async def get_user_bookmark_ids(self, user_id: int) -> list[int]:
        return await self.repo.get_user_bookmark_ids(user_id)

    async def check_bookmark(self, user_id: int, vacancy_id: int) -> bool:
        bookmark = await self.repo.get_by_user_and_vacancy(user_id, vacancy_id)
        return bookmark is not None

    async def toggle_bookmark(self, user_id: int, vacancy_id: int) -> dict[str, bool | int]:
        existing = await self.repo.get_by_user_and_vacancy(user_id, vacancy_id)

        if existing:
            await self.repo.delete_by_user_and_vacancy(user_id, vacancy_id)
            return {"bookmarked": False, "vacancy_id": vacancy_id}
        else:
            bookmark_model = Bookmark(user_id=user_id, vacancy_id=vacancy_id)
            await self.repo.create(bookmark_model)
            return {"bookmarked": True, "vacancy_id": vacancy_id}

    async def delete_bookmark(self, bookmark_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(bookmark_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Bookmark not found")
        return {"deleted": True, "bookmark_id": bookmark_id}
