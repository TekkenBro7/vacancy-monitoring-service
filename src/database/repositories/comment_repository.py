from src.database.repositories.base_repository import BaseRepository
from src.models.comments import Comment


class CommentRepository(BaseRepository[Comment]):
    pass
