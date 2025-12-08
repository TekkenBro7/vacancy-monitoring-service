from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Country(BaseModel):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    cities: Mapped[list["City"]] = relationship(
        back_populates="country", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Country id={self.id!r} name={self.name!r}>"


class City(BaseModel):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )

    country: Mapped["Country"] = relationship(back_populates="cities")
    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        back_populates="location", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<City id={self.id!r} name={self.name!r} country_id={self.country_id!r}>"
