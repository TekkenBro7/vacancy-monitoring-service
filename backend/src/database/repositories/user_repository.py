from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.repositories.base_repository import BaseRepository
from src.models.users import User


class UserRepository(BaseRepository[User]):
    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username).options(joinedload(User.role))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
