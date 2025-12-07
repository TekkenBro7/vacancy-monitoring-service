from sqlalchemy import Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class NotificationType(BaseModel):
    __tablename__ = "notification_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    notifications: Mapped[list["Notification"]] = relationship(back_populates="notification_type")

    def __repr__(self) -> str:
        return f"<NotificationType id={self.id!r} name={self.name!r}>"


class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "notification_type_id",
            "message",
            name="uq_user_notification_type_message",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type_id: Mapped[int] = mapped_column(
        ForeignKey("notification_types.id", ondelete="SET NULL"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    notification_type: Mapped["NotificationType"] = relationship(back_populates="notifications")
    user: Mapped["User"] = relationship(  # type: ignore
        back_populates="notifications",
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} user_id={self.user_id} "
            f"type={self.notification_type_id} read={self.is_read}>"
        )
