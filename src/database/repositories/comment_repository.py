from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.comments import Comment


class CommentRepository(BaseRepository[Comment]):
    async def get_by_vacancy_id(self, vacancy_id: int) -> list[Comment]:
        stmt = select(Comment).where(Comment.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
