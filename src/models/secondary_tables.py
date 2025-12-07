from sqlalchemy import Column, ForeignKey, Table

from src.models.base import BaseModel

user_skills_table = Table(
    "user_skills",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

vacancy_skills_table = Table(
    "vacancy_skills",
    BaseModel.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)

comparison_vacancies_table = Table(
    "comparison_vacancies",
    BaseModel.metadata,
    Column("comparison_id", ForeignKey("comparisons.id", ondelete="CASCADE"), primary_key=True),
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
)
