from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from src.services.subscription_service import SubscriptionService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> SubscriptionService:
    return SubscriptionService(db)


@router.get("/", response_model=list[SubscriptionRead])
async def list_subscriptions(
    service: SubscriptionService = Depends(get_service),
) -> list[SubscriptionRead]:
    return await service.list_subscriptions()


@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(
    subscription_id: int,
    service: SubscriptionService = Depends(get_service),
) -> SubscriptionRead:
    return await service.get_subscription(subscription_id)


@router.get("/user/{user_id}", response_model=list[SubscriptionRead])
async def list_user_subscriptions(
    user_id: int,
    service: SubscriptionService = Depends(get_service),
) -> list[SubscriptionRead]:
    return await service.list_user_subscriptions(user_id)


@router.post("/", response_model=SubscriptionRead)
async def create_subscription(
    data: SubscriptionCreate,
    service: SubscriptionService = Depends(get_service),
) -> SubscriptionRead:
    return await service.create_subscription(data)


@router.patch("/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription(
    subscription_id: int,
    data: SubscriptionUpdate,
    service: SubscriptionService = Depends(get_service),
) -> SubscriptionRead:
    return await service.update_subscription(subscription_id, data)


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    service: SubscriptionService = Depends(get_service),
) -> dict[str, bool | int]:
    return await service.delete_subscription(subscription_id)
