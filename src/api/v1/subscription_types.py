from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.subscriptions import (
    SubscriptionTypeCreate,
    SubscriptionTypeRead,
    SubscriptionTypeUpdate,
)
from src.services.subscription_service import SubscriptionTypeService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> SubscriptionTypeService:
    return SubscriptionTypeService(db)


@router.get("/", response_model=list[SubscriptionTypeRead])
async def list_types(
    service: SubscriptionTypeService = Depends(get_service),
) -> list[SubscriptionTypeRead]:
    return await service.list_types()


@router.get("/{type_id}", response_model=SubscriptionTypeRead)
async def get_type(
    type_id: int,
    service: SubscriptionTypeService = Depends(get_service),
) -> SubscriptionTypeRead:
    return await service.get_type(type_id)


@router.post("/", response_model=SubscriptionTypeRead)
async def create_type(
    data: SubscriptionTypeCreate,
    service: SubscriptionTypeService = Depends(get_service),
) -> SubscriptionTypeRead:
    return await service.create_type(data)


@router.patch("/{type_id}", response_model=SubscriptionTypeRead)
async def update_type(
    type_id: int,
    data: SubscriptionTypeUpdate,
    service: SubscriptionTypeService = Depends(get_service),
) -> SubscriptionTypeRead:
    return await service.update_type(type_id, data)


@router.delete("/{type_id}")
async def delete_type(
    type_id: int,
    service: SubscriptionTypeService = Depends(get_service),
) -> dict[str, bool | int]:
    return await service.delete_type(type_id)
