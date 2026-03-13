from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.secondary_tables import comparison_vacancies_table, vacancy_skills_table


class Company(BaseModel):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name})>"


class Vacancy(BaseModel):
    __tablename__ = "vacancies"
    __table_args__ = (UniqueConstraint("source_id", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    salary_from: Mapped[int] = mapped_column(nullable=True)
    salary_to: Mapped[int] = mapped_column(nullable=True)

    external_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    experience: Mapped[str] = mapped_column(String(100), nullable=True)

    employment: Mapped[str] = mapped_column(String(50), nullable=True)
    schedule: Mapped[str] = mapped_column(String(50), nullable=True)
    vacancy_url: Mapped[str] = mapped_column(String(255), nullable=True)

    is_remote: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)

    created_at_source: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,  # ← Как в BaseModel!
    )
    published_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    fingerprint: Mapped[str] = mapped_column(String(64), index=True)

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
    company: Mapped["Company"] = relationship(back_populates="vacancies")
    skills: Mapped[list["Skill"]] = relationship(  # type: ignore
        secondary=vacancy_skills_table, back_populates="vacancies"
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
    comparisons: Mapped[list["Comparison"]] = relationship(  # type: ignore
        secondary=comparison_vacancies_table, back_populates="vacancies"
    )

    def __repr__(self) -> str:
        return f"<Vacancy(id={self.id}, title={self.title}, company_id={self.company_id})>"
