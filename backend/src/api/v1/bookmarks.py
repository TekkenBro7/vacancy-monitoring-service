from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.bookmarks import BookmarkCreate, BookmarkRead
from src.services.bookmark_service import BookmarkService

router = APIRouter()


def get_bookmark_service(
    db: AsyncSession = Depends(get_async_session),
) -> BookmarkService:
    return BookmarkService(db)


@router.get("/user/{user_id}/", response_model=list[BookmarkRead])
async def list_user_bookmarks(
    user_id: int,
    service: BookmarkService = Depends(get_bookmark_service),
) -> list[BookmarkRead]:
    return await service.list_user_bookmarks(user_id)


@router.post("/", response_model=BookmarkRead)
async def create_bookmark(
    data: BookmarkCreate,
    service: BookmarkService = Depends(get_bookmark_service),
) -> BookmarkRead:
    return await service.create_bookmark(data)


@router.delete("/{bookmark_id}/")
async def delete_bookmark(
    bookmark_id: int,
    service: BookmarkService = Depends(get_bookmark_service),
) -> dict[str, bool | int]:
    return await service.delete_bookmark(bookmark_id)
