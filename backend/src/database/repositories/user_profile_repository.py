from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.users import UserProfile


class UserProfileRepository(BaseRepository[UserProfile]):
    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        query = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                selectinload(UserProfile.city),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[UserProfile]:
        query = (
            select(UserProfile).options(selectinload(UserProfile.city)).offset(skip).limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
