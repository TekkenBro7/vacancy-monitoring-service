from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.user_profile_repository import UserProfileRepository
from src.database.repositories.user_repository import UserRepository
from src.models.users import User, UserProfile
from src.schemas.users import UserCreate, UserMe, UserRead, UserUpdate
from src.utils.security import hash_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(User, db)
        self.user_profile_repo = UserProfileRepository(UserProfile, db)

    async def list_users(self) -> list[UserRead]:
        users = await self.user_repo.list()
        return [UserRead.model_validate(u) for u in users]

    async def get_user(self, user_id: int) -> UserRead:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        return UserRead.model_validate(user)

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.user_repo.get_by_username(username)

    async def get_user_me(self, user_id: int) -> UserMe | None:
        user = await self.user_repo.get_user_with_role(user_id)

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        return UserMe(username=user.username, role_name=user.role.name)

    async def create_user(self, data: UserCreate) -> UserRead:
        try:
            user_model = User(
                username=data.username,
                email=data.email,
                role_id=data.role_id,
                password_hash=hash_password(data.password),
            )

            user = await self.user_repo.create(user_model)

            profile = UserProfile(user_id=user.id)
            await self.user_profile_repo.create(profile)

            return UserRead.model_validate(user)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="User with this username or email already exists",
            ) from e

    async def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password":
                user.password_hash = hash_password(value)
            else:
                setattr(user, key, value)

        try:
            updated = await self.user_repo.update(user)
            return UserRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists",
            ) from e

    async def delete_user(self, user_id: int) -> dict[str, bool | int]:
        deleted = await self.user_repo.delete_by_id(user_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        return {"deleted": True, "user_id": user_id}
