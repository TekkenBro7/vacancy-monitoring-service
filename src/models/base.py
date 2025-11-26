from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class BaseModel(Base):
    __abstract__ = True

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
