from typing import TypeVar

from sqlalchemy import delete, select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository[T]:
    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> T | None:
        stmt = select(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: dict) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: dict) -> T | None:
        stmt = (
            sqlalchemy_update(self.model)
            .values(**data)
            .where(self.model.id == id)  # type: ignore
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete_by_id(self, id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0  # type: ignore
