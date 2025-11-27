from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type_id: Mapped[int] = mapped_column(
        ForeignKey("source_types.id", ondelete="SET NULL"), nullable=False
    )

    source_type: Mapped["SourceType"] = relationship(back_populates="sources")
    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name={self.name}, url={self.source_url})>"
