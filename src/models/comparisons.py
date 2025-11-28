from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Comparison(BaseModel):
    __tablename__ = "comparisons"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    vacancies: Mapped[list["ComparisonVacancy"]] = relationship(
        back_populates="comparison", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(back_populates="comparisons")  # type: ignore

    def __repr__(self) -> str:
        return f"<Comparison id={self.id} user_id={self.user_id} name={self.name}>"


class ComparisonVacancy(BaseModel):
    __tablename__ = "comparison_vacancies"

    comparison_id: Mapped[int] = mapped_column(
        ForeignKey("comparisons.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    comparison: Mapped["Comparison"] = relationship(back_populates="vacancies")

    def __repr__(self) -> str:
        return f"Comparison_id={self.comparison_id} vacancy_id={self.vacancy_id}>"
