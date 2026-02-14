from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.repositories.base_repository import BaseRepository
from src.models.users import User


class UserRepository(BaseRepository[User]):
    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username).options(joinedload(User.role))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_with_role(self, user_id: int) -> User | None:
        query = select(User).options(joinedload(User.role)).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        query = select(User).where(User.google_id == google_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
