from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.comments import CommentCreate, CommentRead, CommentUpdate
from src.services.comment_service import CommentService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> CommentService:
    return CommentService(db)


@router.get("/", response_model=list[CommentRead])
async def list_comments(service: CommentService = Depends(get_service)) -> list[CommentRead]:
    return await service.list_comments()


@router.get("/{comment_id}/", response_model=CommentRead)
async def get_comment(
    comment_id: int, service: CommentService = Depends(get_service)
) -> CommentRead:
    return await service.get_comment(comment_id)


@router.get("/vacancy/{vacancy_id}/", response_model=list[CommentRead])
async def list_vacancy_comments(
    vacancy_id: int, service: CommentService = Depends(get_service)
) -> list[CommentRead]:
    return await service.list_vacancy_comments(vacancy_id)


@router.post("/", response_model=CommentRead)
async def create_comment(
    data: CommentCreate, service: CommentService = Depends(get_service)
) -> CommentRead:
    return await service.create_comment(data)


@router.patch("/{comment_id}/", response_model=CommentRead)
async def update_comment(
    comment_id: int, data: CommentUpdate, service: CommentService = Depends(get_service)
) -> CommentRead:
    return await service.update_comment(comment_id, data)


@router.delete("/{comment_id}/")
async def delete_comment(
    comment_id: int, service: CommentService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_comment(comment_id)
