from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.comments import Comment


class CommentRepository(BaseRepository[Comment]):
    async def get_by_vacancy_id(self, vacancy_id: int) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.vacancy_id == vacancy_id)
            .options(selectinload(Comment.user))
            .order_by(Comment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_with_user(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.user))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vacancy_stats(self, vacancy_id: int) -> dict[str, float | int]:
        result = await self.session.execute(
            select(func.avg(Comment.rating), func.count(Comment.id)).where(
                Comment.vacancy_id == vacancy_id
            )
        )
        avg_rating, count = result.one()
        return {
            "avg_rating": round(float(avg_rating), 2) if avg_rating is not None else 0.0,
            "total_comments": count or 0,
        }
