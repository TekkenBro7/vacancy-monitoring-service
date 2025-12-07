from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.subscriptions import (
    SubscriptionTargetCreate,
    SubscriptionTargetRead,
    SubscriptionTargetUpdate,
)
from src.services.subscription_service import SubscriptionTargetService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> SubscriptionTargetService:
    return SubscriptionTargetService(db)


@router.get("/", response_model=list[SubscriptionTargetRead])
async def list_targets(
    service: SubscriptionTargetService = Depends(get_service),
) -> list[SubscriptionTargetRead]:
    return await service.list_targets()


@router.get("/{target_id}", response_model=SubscriptionTargetRead)
async def get_target(
    target_id: int,
    service: SubscriptionTargetService = Depends(get_service),
) -> SubscriptionTargetRead:
    return await service.get_target(target_id)


@router.post("/", response_model=SubscriptionTargetRead)
async def create_target(
    data: SubscriptionTargetCreate,
    service: SubscriptionTargetService = Depends(get_service),
) -> SubscriptionTargetRead:
    return await service.create_target(data)


@router.patch("/{target_id}", response_model=SubscriptionTargetRead)
async def update_target(
    target_id: int,
    data: SubscriptionTargetUpdate,
    service: SubscriptionTargetService = Depends(get_service),
) -> SubscriptionTargetRead:
    return await service.update_target(target_id, data)


@router.delete("/{target_id}")
async def delete_target(
    target_id: int,
    service: SubscriptionTargetService = Depends(get_service),
) -> dict[str, bool | int]:
    return await service.delete_target(target_id)
