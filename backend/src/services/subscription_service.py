from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.subscription_repository import SubscriptionRepository
from src.database.repositories.subscription_target_repository import SubscriptionTargetRepository
from src.database.repositories.subscription_type_repository import SubscriptionTypeRepository
from src.models.subscriptions import Subscription, SubscriptionTarget, SubscriptionType
from src.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionTargetCreate,
    SubscriptionTargetRead,
    SubscriptionTargetUpdate,
    SubscriptionTypeCreate,
    SubscriptionTypeRead,
    SubscriptionTypeUpdate,
    SubscriptionUpdate,
)


class SubscriptionTargetService:
    def __init__(self, db: AsyncSession):
        self.repo = SubscriptionTargetRepository(SubscriptionTarget, db)

    async def list_targets(self) -> list[SubscriptionTargetRead]:
        items = await self.repo.list()
        return [SubscriptionTargetRead.model_validate(i) for i in items]

    async def get_target(self, target_id: int) -> SubscriptionTargetRead:
        obj = await self.repo.get_by_id(target_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription target not found")
        return SubscriptionTargetRead.model_validate(obj)

    async def create_target(self, data: SubscriptionTargetCreate) -> SubscriptionTargetRead:
        try:
            obj = SubscriptionTarget(name=data.name)
            created = await self.repo.create(obj)
            return SubscriptionTargetRead.model_validate(created)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Target with this name already exists"
            ) from e

    async def update_target(
        self, target_id: int, data: SubscriptionTargetUpdate
    ) -> SubscriptionTargetRead:
        obj = await self.repo.get_by_id(target_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription target not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            return SubscriptionTargetRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Target update violates constraints"
            ) from e

    async def delete_target(self, target_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(target_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription target not found")

        return {"deleted": True, "target_id": target_id}


class SubscriptionTypeService:
    def __init__(self, db: AsyncSession):
        self.repo = SubscriptionTypeRepository(SubscriptionType, db)

    async def list_types(self) -> list[SubscriptionTypeRead]:
        items = await self.repo.list()
        return [SubscriptionTypeRead.model_validate(i) for i in items]

    async def get_type(self, type_id: int) -> SubscriptionTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription type not found")
        return SubscriptionTypeRead.model_validate(obj)

    async def create_type(self, data: SubscriptionTypeCreate) -> SubscriptionTypeRead:
        try:
            obj = SubscriptionType(name=data.name, description=data.description)
            created = await self.repo.create(obj)
            return SubscriptionTypeRead.model_validate(created)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Subscription type name already exists"
            ) from e

    async def update_type(self, type_id: int, data: SubscriptionTypeUpdate) -> SubscriptionTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription type not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)

        try:
            updated = await self.repo.update(obj)
            return SubscriptionTypeRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Type update violates constraints") from e

    async def delete_type(self, type_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(type_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription type not found")

        return {"deleted": True, "type_id": type_id}


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.repo = SubscriptionRepository(Subscription, db)

    async def list_subscriptions(self) -> list[SubscriptionRead]:
        subs = await self.repo.list()
        return [SubscriptionRead.model_validate(s) for s in subs]

    async def get_subscription(self, subscription_id: int) -> SubscriptionRead:
        sub = await self.repo.get_by_id(subscription_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription not found")
        return SubscriptionRead.model_validate(sub)

    async def list_user_subscriptions(self, user_id: int) -> list[SubscriptionRead]:
        result = await self.repo.get_by_user_id(user_id)
        return [SubscriptionRead.model_validate(s) for s in result]

    async def create_subscription(self, data: SubscriptionCreate) -> SubscriptionRead:
        try:
            obj = Subscription(
                user_id=data.user_id,
                subscription_type_id=data.subscription_type_id,
                target_type_id=data.target_type_id,
            )
            created = await self.repo.create(obj)
            return SubscriptionRead.model_validate(created)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Invalid user or subscription type/target"
            ) from e

    async def update_subscription(
        self, subscription_id: int, data: SubscriptionUpdate
    ) -> SubscriptionRead:
        sub = await self.repo.get_by_id(subscription_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(sub, k, v)

        try:
            updated = await self.repo.update(sub)
            return SubscriptionRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Subscription update violates constraints"
            ) from e

    async def delete_subscription(self, subscription_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(subscription_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription not found")

        return {"deleted": True, "subscription_id": subscription_id}
