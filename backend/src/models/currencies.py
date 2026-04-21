from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Currency(BaseModel):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    symbol: Mapped[str | None] = mapped_column(String(16), nullable=True, unique=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        back_populates="currency", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Currency id={self.id} name={self.name} symbol={self.symbol}>"
