from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class City(BaseModel):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(  # type: ignore
        back_populates="location", cascade="all, delete-orphan"
    )
    user_profiles: Mapped[list["UserProfile"]] = relationship(back_populates="city")  # type: ignore

    def __repr__(self) -> str:
        return f"<City id={self.id!r} name={self.name!r}>"
