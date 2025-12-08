from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.subscriptions import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    async def get_by_user_id(self, user_id: int) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
