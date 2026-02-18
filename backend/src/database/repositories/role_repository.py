from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.users import Role


class RoleRepository(BaseRepository[Role]):
    async def get_by_name(self, name: str) -> Role | None:
        query = select(Role).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
