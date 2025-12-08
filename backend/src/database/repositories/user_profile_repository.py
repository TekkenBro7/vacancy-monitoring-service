from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.users import UserProfile


class UserProfileRepository(BaseRepository[UserProfile]):
    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
