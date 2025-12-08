from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.services.user_service import UserService

router = APIRouter()


def get_user_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(db)


@router.get("/", response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_user_service)) -> list[UserRead]:
    return await service.list_users()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.get_user(user_id)


@router.post("/", response_model=UserRead)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create_user(data)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.update_user(user_id, data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> dict[str, bool | int]:
    return await service.delete_user(user_id)
