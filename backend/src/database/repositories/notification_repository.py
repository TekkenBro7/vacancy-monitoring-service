from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.notifications import Notification


class NotificationRepository(BaseRepository[Notification]):
    async def get_by_user_id(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
