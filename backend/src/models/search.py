from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class SearchQuery(BaseModel):
    __tablename__ = "search_queries"
    __table_args__ = (UniqueConstraint("user_id", "query_text", name="uq_user_query"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="search_queries")  # type: ignore

    def __repr__(self) -> str:
        return f"<SearchQuery id={self.id} user_id={self.user_id}>"
