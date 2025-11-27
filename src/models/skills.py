from sqlalchemy import ForeignKey, String
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


class UserSkill(BaseModel):
    __tablename__ = "user_skills"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserSkill(user_id={self.user_id}, skill_id={self.skill_id})>"


class VacancySkill(BaseModel):
    __tablename__ = "vacancy_skills"

    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id"), primary_key=True, nullable=False
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True, nullable=False)

    def __repr__(self) -> str:
        return f"<VacancySkill(vacancy_id={self.vacancy_id}, skill_id={self.skill_id})>"
