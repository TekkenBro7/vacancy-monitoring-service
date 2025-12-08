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
            bookmark_model = Bookmark(
                user_id=data.user_id,
                vacancy_id=data.vacancy_id,
            )

            bookmark = await self.repo.create(bookmark_model)
            return BookmarkRead.model_validate(bookmark)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Bookmark create conflict") from e

    async def list_user_bookmarks(self, user_id: int) -> list[BookmarkRead]:
        items = await self.repo.get_by_user_id(user_id)
        return [BookmarkRead.model_validate(i) for i in items]

    async def delete_bookmark(self, bookmark_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(bookmark_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Bookmark not found")
        return {"deleted": True, "bookmark_id": bookmark_id}
