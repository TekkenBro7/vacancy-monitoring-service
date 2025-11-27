from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Bookmark(BaseModel):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="bookmarks")  # type: ignore
    vacancy: Mapped["Vacancy"] = relationship(back_populates="bookmarks")  # type: ignore

    def __repr__(self) -> str:
        return f"<Bookmark id={self.id} user_id={self.user_id} vacancy_id={self.vacancy_id}>"
