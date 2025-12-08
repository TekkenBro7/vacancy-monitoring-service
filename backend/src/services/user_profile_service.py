from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.user_profile_repository import UserProfileRepository
from src.models.users import UserProfile
from src.schemas.user_profiles import UserProfileRead, UserProfileUpdate


class UserProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = UserProfileRepository(UserProfile, db)

    async def list_profiles(self) -> list[UserProfileRead]:
        profiles = await self.repo.list()
        return [UserProfileRead.model_validate(p) for p in profiles]

    async def get_profile(self, user_id: int) -> UserProfileRead:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile for user {user_id} not found",
            )
        return UserProfileRead.model_validate(profile)

    async def update_profile(self, user_id: int, data: UserProfileUpdate) -> UserProfileRead:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile for user {user_id} not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)

        try:
            updated = await self.repo.update(profile)
            return UserProfileRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Failed to update profile") from e
