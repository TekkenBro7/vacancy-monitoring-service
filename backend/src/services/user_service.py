from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.database.repositories.role_repository import RoleRepository
from src.database.repositories.user_profile_repository import UserProfileRepository
from src.database.repositories.user_repository import UserRepository
from src.models.users import Role, User, UserProfile
from src.schemas.users import UserAdminCreate, UserCreate, UserMe, UserRead, UserUpdate
from src.utils.security import hash_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(User, db)
        self.user_profile_repo = UserProfileRepository(UserProfile, db)
        self.role_repo = RoleRepository(Role, db)

    async def _get_user_role_id(self) -> int:
        role = await self.role_repo.get_by_name("user")
        if not role:
            raise HTTPException(status.HTTP_500_INTERNAL_ERROR, "Role 'user' not found")
        return role.id

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

        return UserMe(id=user.id, username=user.username, role_name=user.role.name)

    async def create_user(self, data: UserCreate) -> UserRead:
        try:
            role_id = await self._get_user_role_id()

            user_model = User(
                username=data.username,
                email=data.email,
                role_id=role_id,
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

    async def create_user_with_role(self, data: UserAdminCreate) -> UserRead:
        try:
            role = await self.role_repo.get_by_id(data.role_id)
            if not role:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"Role with id {data.role_id} not found"
                )

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

    async def get_by_google_id(self, google_id: str) -> User | None:
        logger.info("Searching user by google_id=%s", google_id)
        return await self.user_repo.get_by_google_id(google_id)

    async def get_by_email(self, email: str) -> User | None:
        logger.info("Searching user by email=%s", email)
        return await self.user_repo.get_by_email(email)

    async def create_google_user(
        self,
        email: str,
        google_id: str,
        name: str,
    ) -> User:
        try:
            logger.info("Creating new Google user: %s", email)

            role_id = await self._get_user_role_id()

            user = User(
                username=name,
                email=email,
                google_id=google_id,
                role_id=role_id,
                password_hash=None,
            )

            user = await self.user_repo.create(user)
            await self.user_profile_repo.create(UserProfile(user_id=user.id))

            return user

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "User create error",
            ) from e

    async def attach_google_account(self, user: User, google_id: str) -> User:
        logger.info("Attaching google_id=%s to user_id=%s", google_id, user.id)

        user.google_id = google_id
        return await self.user_repo.update(user)
