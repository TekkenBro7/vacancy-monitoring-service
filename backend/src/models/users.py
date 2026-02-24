from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.secondary_tables import user_skills_table


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(unique=True, nullable=True)

    role: Mapped["Role"] = relationship(back_populates="users")
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)
    skills: Mapped[list["Skill"]] = relationship(  # type: ignore
        secondary=user_skills_table, back_populates="users", lazy="selectin"
    )
    notifications: Mapped[list["Notification"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
    comparisons: Mapped[list["Comparison"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
    search_queries: Mapped[list["SearchQuery"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    desired_salary: Mapped[int] = mapped_column(nullable=True)
    desired_position: Mapped[str] = mapped_column(String(100), nullable=True)
    desired_salary_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="profile")
    desired_salary_currency: Mapped["Currency"] = relationship(back_populates="user_profiles")  # type: ignore

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, full_name={self.full_name})>"
