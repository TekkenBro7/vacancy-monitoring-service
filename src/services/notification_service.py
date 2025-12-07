from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.notification_repository import NotificationRepository
from src.database.repositories.notification_type_repository import NotificationTypeRepository
from src.models.notifications import Notification, NotificationType
from src.schemas.notifications import (
    NotificationCreate,
    NotificationRead,
    NotificationTypeCreate,
    NotificationTypeRead,
    NotificationTypeUpdate,
    NotificationUpdate,
)


class NotificationTypeService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationTypeRepository(NotificationType, db)

    async def list_types(self) -> list[NotificationTypeRead]:
        items = await self.repo.list()
        return [NotificationTypeRead.model_validate(i) for i in items]

    async def get_type(self, type_id: int) -> NotificationTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification type not found")
        return NotificationTypeRead.model_validate(obj)

    async def create_type(self, data: NotificationTypeCreate) -> NotificationTypeRead:
        try:
            obj = NotificationType(name=data.name, description=data.description)
            created = await self.repo.create(obj)
            return NotificationTypeRead.model_validate(created)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Notification type already exists") from e

    async def update_type(self, type_id: int, data: NotificationTypeUpdate) -> NotificationTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification type not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            return NotificationTypeRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Uniqueness conflict") from e

    async def delete_type(self, type_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(type_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification type not found")
        return {"deleted": True, "type_id": type_id}


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationRepository(Notification, db)

    async def list_notifications(self) -> list[NotificationRead]:
        items = await self.repo.list()
        return [NotificationRead.model_validate(i) for i in items]

    async def get_notification(self, notification_id: int) -> NotificationRead:
        obj = await self.repo.get_by_id(notification_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return NotificationRead.model_validate(obj)

    async def list_user_notifications(self, user_id: int) -> list[NotificationRead]:
        items = await self.repo.get_by_user_id(user_id)
        return [NotificationRead.model_validate(i) for i in items]

    async def create_notification(self, data: NotificationCreate) -> NotificationRead:
        try:
            obj = Notification(
                user_id=data.user_id,
                notification_type_id=data.notification_type_id,
                message=data.message,
                subscription_id=data.subscription_id,
            )
            created = await self.repo.create(obj)
            return NotificationRead.model_validate(created)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Notification create conflict") from e

    async def update_notification(
        self, notification_id: int, data: NotificationUpdate
    ) -> NotificationRead:
        obj = await self.repo.get_by_id(notification_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            return NotificationRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Uniqueness conflict") from e

    async def delete_notification(self, notification_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(notification_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return {"deleted": True, "notification_id": notification_id}
