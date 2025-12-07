from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.notifications import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from src.services.notification_service import NotificationService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> NotificationService:
    return NotificationService(db)


@router.get("/", response_model=list[NotificationRead])
async def list_notifications(
    service: NotificationService = Depends(get_service),
) -> list[NotificationRead]:
    return await service.list_notifications()


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: int, service: NotificationService = Depends(get_service)
) -> NotificationRead:
    return await service.get_notification(notification_id)


@router.get("/user/{user_id}", response_model=list[NotificationRead])
async def list_user_notifications(
    user_id: int, service: NotificationService = Depends(get_service)
) -> list[NotificationRead]:
    return await service.list_user_notifications(user_id)


@router.post("/", response_model=NotificationRead)
async def create_notification(
    data: NotificationCreate,
    service: NotificationService = Depends(get_service),
) -> NotificationRead:
    return await service.create_notification(data)


@router.patch("/{notification_id}", response_model=NotificationRead)
async def update_notification(
    notification_id: int,
    data: NotificationUpdate,
    service: NotificationService = Depends(get_service),
) -> NotificationRead:
    return await service.update_notification(notification_id, data)


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int, service: NotificationService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_notification(notification_id)
