from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.dependencies.users import get_current_user
from src.models.users import User
from src.schemas.bookmarks import BookmarkCreate, BookmarkRead
from src.services.bookmark_service import BookmarkService

router = APIRouter()


def get_bookmark_service(
    db: AsyncSession = Depends(get_async_session),
) -> BookmarkService:
    return BookmarkService(db)


@router.get("/", response_model=list[BookmarkRead])
async def list_my_bookmarks(
    current_user: User = Depends(get_current_user),
    service: BookmarkService = Depends(get_bookmark_service),
) -> list[BookmarkRead]:
    return await service.list_user_bookmarks(current_user.id)


@router.get("/ids/", response_model=list[int])
async def get_my_bookmark_ids(
    current_user: User = Depends(get_current_user),
    service: BookmarkService = Depends(get_bookmark_service),
) -> list[int]:
    return await service.get_user_bookmark_ids(current_user.id)


@router.get("/check/{vacancy_id}/")
async def check_bookmark(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    service: BookmarkService = Depends(get_bookmark_service),
) -> dict[str, bool]:
    is_bookmarked = await service.check_bookmark(current_user.id, vacancy_id)
    return {"bookmarked": is_bookmarked}


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


@router.post("/toggle/{vacancy_id}/")
async def toggle_bookmark(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    service: BookmarkService = Depends(get_bookmark_service),
) -> dict[str, bool | int]:
    return await service.toggle_bookmark(current_user.id, vacancy_id)


@router.delete("/{bookmark_id}/")
async def delete_bookmark(
    bookmark_id: int,
    service: BookmarkService = Depends(get_bookmark_service),
) -> dict[str, bool | int]:
    return await service.delete_bookmark(bookmark_id)
