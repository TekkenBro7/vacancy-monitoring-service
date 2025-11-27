from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class SubscriptionTarget(BaseModel):
    __tablename__ = "subscription_targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="target_type", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SubscriptionTarget id={self.id} name={self.name}>"


class SubscriptionType(BaseModel):
    __tablename__ = "subscription_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="subscription_type",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SubscriptionType id={self.id} name={self.name}>"


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subscription_type_id: Mapped[int] = mapped_column(
        ForeignKey("subscription_types.id", ondelete="SET NULL"), nullable=False
    )
    target_type_id: Mapped[int] = mapped_column(
        ForeignKey("subscription_targets.id", ondelete="SET NULL"), nullable=False
    )

    subscription_type: Mapped["SubscriptionType"] = relationship(back_populates="subscriptions")
    target_type: Mapped["SubscriptionTarget"] = relationship(back_populates="subscriptions")
    user: Mapped["User"] = relationship(back_populates="subscriptions")  # type: ignore

    def __repr__(self) -> str:
        return (
            f"<Subscription id={self.id!r} "
            f"user_id={self.user_id!r} "
            f"type={self.subscription_type_id!r} "
            f"target={self.target_type_id}>"
        )
