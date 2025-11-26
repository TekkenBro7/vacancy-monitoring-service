from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()

    role: Mapped["Role"] = relationship(back_populates="users")
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    desired_position: Mapped[str] = mapped_column(nullable=True)
    desired_salary: Mapped[int] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
