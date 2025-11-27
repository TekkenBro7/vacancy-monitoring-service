from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Comment(BaseModel):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="comments")  # type: ignore
    vacancy: Mapped["Vacancy"] = relationship(back_populates="comments")  # type: ignore

    def __repr__(self) -> str:
        return (
            f"<Comment id={self.id!r} user_id={self.user_id!r} "
            f"vacancy_id={self.vacancy_id!r} rating={self.rating!r}>"
        )
