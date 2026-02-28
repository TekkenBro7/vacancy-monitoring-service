from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.notifications import (
    NotificationTypeCreate,
    NotificationTypeRead,
    NotificationTypeUpdate,
)
from src.services.notification_service import NotificationTypeService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> NotificationTypeService:
    return NotificationTypeService(db)


@router.get("/", response_model=list[NotificationTypeRead])
async def list_types(
    service: NotificationTypeService = Depends(get_service),
) -> list[NotificationTypeRead]:
    return await service.list_types()


@router.get("/{type_id}/", response_model=NotificationTypeRead)
async def get_type(
    type_id: int, service: NotificationTypeService = Depends(get_service)
) -> NotificationTypeRead:
    return await service.get_type(type_id)


@router.post("/", response_model=NotificationTypeRead)
async def create_type(
    data: NotificationTypeCreate,
    service: NotificationTypeService = Depends(get_service),
) -> NotificationTypeRead:
    return await service.create_type(data)


@router.patch("/{type_id}/", response_model=NotificationTypeRead)
async def update_type(
    type_id: int,
    data: NotificationTypeUpdate,
    service: NotificationTypeService = Depends(get_service),
) -> NotificationTypeRead:
    return await service.update_type(type_id, data)


@router.delete("/{type_id}/")
async def delete_type(
    type_id: int, service: NotificationTypeService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_type(type_id)
