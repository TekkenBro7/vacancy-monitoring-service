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
        obj = await self.repo.get_by_id(comment_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
        return CommentRead.model_validate(obj)

    async def list_vacancy_comments(self, vacancy_id: int) -> list[CommentRead]:
        items = await self.repo.get_by_vacancy_id(vacancy_id)
        return [CommentRead.model_validate(i) for i in items]

    async def create_comment(self, data: CommentCreate) -> CommentRead:
        try:
            comment_model = Comment(
                user_id=data.user_id,
                vacancy_id=data.vacancy_id,
                content=data.content,
                rating=data.rating,
            )
            created = await self.repo.create(comment_model)
            return CommentRead.model_validate(created)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Сomment create conflict") from e

    async def update_comment(self, comment_id: int, data: CommentUpdate) -> CommentRead:
        obj = await self.repo.get_by_id(comment_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            return CommentRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Comment update conflict") from e

    async def delete_comment(self, comment_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(comment_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
        return {"deleted": True, "comment_id": comment_id}
