from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.comment_repository import CommentRepository
from src.models.comments import Comment
from src.schemas.comments import CommentCreate, CommentRead, CommentUpdate


class CommentService:
    def __init__(self, db: AsyncSession):
        self.repo = CommentRepository(Comment, db)

    async def list_comments(self) -> list[CommentRead]:
        items = await self.repo.list()
        return [CommentRead.model_validate(i) for i in items]

    async def get_comment(self, comment_id: int) -> CommentRead:
        obj = await self.repo.get_by_id_with_user(comment_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
        return CommentRead.model_validate(obj)

    async def list_vacancy_comments(self, vacancy_id: int) -> list[CommentRead]:
        items = await self.repo.get_by_vacancy_id(vacancy_id)
        return [CommentRead.model_validate(i) for i in items]

    async def get_vacancy_stats(self, vacancy_id: int) -> dict[str, float | int]:
        return await self.repo.get_vacancy_stats(vacancy_id)

    async def create_comment(self, user_id: int, data: CommentCreate) -> CommentRead:
        try:
            comment_model = Comment(
                user_id=user_id,
                vacancy_id=data.vacancy_id,
                content=data.content,
                rating=data.rating,
            )
            created = await self.repo.create(comment_model)

            obj = await self.repo.get_by_id_with_user(created.id)
            return CommentRead.model_validate(obj)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Сomment create conflict") from e

    async def update_comment(
        self, comment_id: int, user_id: int, data: CommentUpdate
    ) -> CommentRead:
        obj = await self.repo.get_by_id_with_user(comment_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

        if obj.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only edit your own comments")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            obj = await self.repo.get_by_id_with_user(updated.id)
            return CommentRead.model_validate(obj)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Comment update conflict") from e

    async def delete_comment(
        self, comment_id: int, user_id: int, is_admin: bool = False
    ) -> dict[str, bool | int]:
        obj = await self.repo.get_by_id(comment_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

        if obj.user_id != user_id and not is_admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only delete your own comments")

        await self.repo.delete_by_id(comment_id)
        return {"deleted": True, "comment_id": comment_id}
