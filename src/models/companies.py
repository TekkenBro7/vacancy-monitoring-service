from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name})>"


class Vacancy(BaseModel):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    salary_from: Mapped[int] = mapped_column(nullable=True)
    salary_to: Mapped[int] = mapped_column(nullable=True)
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="SET NULL"), nullable=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"), nullable=True
    )
    vacancy_url: Mapped[str] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=True)

    company: Mapped["Company"] = relationship(back_populates="vacancies")
    skills: Mapped[list["Skill"]] = relationship(  # type: ignore
        secondary="vacancy_skills", back_populates="vacancies"
    )
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        back_populates="vacancy", cascade="all, delete-orphan"
    )
    currency: Mapped["Currency"] = relationship(back_populates="vacancies")  # type: ignore
    source: Mapped["Source"] = relationship(back_populates="vacancies")  # type: ignore
    location: Mapped["City"] = relationship(back_populates="vacancies")  # type: ignore
    bookmarks: Mapped[list["Bookmark"]] = relationship(  # type: ignore
        back_populates="vacancy", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Vacancy(id={self.id}, title={self.title}, company_id={self.company_id})>"
