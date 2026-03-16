from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from sqlalchemy import Date

from src.core.enums import SourceParseTaskStatus
from src.models.base import BaseModel


class SourceType(BaseModel):
    __tablename__ = "source_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    sources: Mapped[list["Source"]] = relationship(
        back_populates="source_type", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SourceType(id={self.id}, type_name={self.type_name})>"


class Source(BaseModel):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("name", "source_url", name="uq_source_name_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type_id: Mapped[int] = mapped_column(
        ForeignKey("source_types.id", ondelete="SET NULL"), nullable=False
    )
    
    last_successful_parse_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    source_type: Mapped["SourceType"] = relationship(back_populates="sources")
    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        back_populates="source", cascade="all, delete-orphan"
    )
    parse_tasks: Mapped[list["SourceParseTask"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name={self.name}, url={self.source_url})>"


class SourceParseTask(BaseModel):
    __tablename__ = "source_parse_tasks"
    __table_args__ = (
        UniqueConstraint("source_id", "parse_date", name="uq_source_parse_task_source_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    parse_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SourceParseTaskStatus.PENDING.value,
        index=True,
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source: Mapped["Source"] = relationship(
        back_populates="parse_tasks",
    )

    def __repr__(self) -> str:
        return (
            f"<SourceParseTask(id={self.id}, source_id={self.source_id}, "
            f"parse_date={self.parse_date}, status={self.status})>"
        )