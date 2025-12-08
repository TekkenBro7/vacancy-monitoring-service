from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Skill(BaseModel):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(secondary="user_skills", back_populates="skills")  # type: ignore
    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        secondary="vacancy_skills", back_populates="skills"
    )

    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name={self.name})>"
