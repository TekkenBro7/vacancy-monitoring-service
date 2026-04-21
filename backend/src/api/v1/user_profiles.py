from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.user_profiles import ProfileOptionsResponse, UserProfileRead, UserProfileUpdate
from src.services.user_profile_service import UserProfileService

router = APIRouter()


def get_user_profile_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserProfileService:
    return UserProfileService(db)


@router.get("/options/", response_model=ProfileOptionsResponse)
async def get_profile_options() -> ProfileOptionsResponse:
    return UserProfileService.get_profile_options()


@router.get("/", response_model=list[UserProfileRead])
async def list_profiles(db: AsyncSession = Depends(get_async_session)) -> list[UserProfileRead]:
    service = UserProfileService(db)
    return await service.list_profiles()


@router.get("/{user_id}/", response_model=UserProfileRead)
async def get_profile(
    user_id: int,
    service: UserProfileService = Depends(get_user_profile_service),
) -> UserProfileRead:
    return await service.get_profile(user_id)


@router.patch("/{user_id}/", response_model=UserProfileRead)
async def update_profile(
    user_id: int,
    data: UserProfileUpdate,
    service: UserProfileService = Depends(get_user_profile_service),
) -> UserProfileRead:
    return await service.update_profile(user_id, data)
