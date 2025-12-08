from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.secondary_tables import comparison_vacancies_table


class Comparison(BaseModel):
    __tablename__ = "comparisons"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        secondary=comparison_vacancies_table, back_populates="comparisons"
    )
    user: Mapped["User"] = relationship(back_populates="comparisons")  # type: ignore

    def __repr__(self) -> str:
        return f"<Comparison id={self.id} user_id={self.user_id} name={self.name}>"
