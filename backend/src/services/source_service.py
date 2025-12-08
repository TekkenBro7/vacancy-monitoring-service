from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.source_type_repository import SourceTypeRepository
from src.models.sources import Source, SourceType
from src.schemas.sources import (
    SourceCreate,
    SourceRead,
    SourceTypeCreate,
    SourceTypeRead,
    SourceTypeUpdate,
    SourceUpdate,
)


class SourceTypeService:
    def __init__(self, db: AsyncSession):
        self.repo = SourceTypeRepository(SourceType, db)

    async def list_source_types(self) -> list[SourceTypeRead]:
        items = await self.repo.list()
        return [SourceTypeRead.model_validate(obj) for obj in items]

    async def get_source_type(self, type_id: int) -> SourceTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SourceType not found")
        return SourceTypeRead.model_validate(obj)

    async def create_source_type(self, data: SourceTypeCreate) -> SourceTypeRead:
        try:
            model = SourceType(type_name=data.type_name, description=data.description)
            obj = await self.repo.create(model)
            return SourceTypeRead.model_validate(obj)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "SourceType already exists") from e

    async def update_source_type(self, type_id: int, data: SourceTypeUpdate) -> SourceTypeRead:
        obj = await self.repo.get_by_id(type_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SourceType not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)

        try:
            updated = await self.repo.update(obj)
            return SourceTypeRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Update conflict: SourceType with this data already exists",
            ) from e

    async def delete_source_type(self, type_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(type_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SourceType not found")
        return {"deleted": True, "source_type_id": type_id}


class SourceService:
    def __init__(self, db: AsyncSession):
        self.repo = SourceRepository(Source, db)

    async def list_sources(self) -> list[SourceRead]:
        items = await self.repo.list()
        return [SourceRead.model_validate(obj) for obj in items]

    async def get_source(self, source_id: int) -> SourceRead:
        obj = await self.repo.get_by_id(source_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Source not found")
        return SourceRead.model_validate(obj)

    async def create_source(self, data: SourceCreate) -> SourceRead:
        try:
            model = Source(
                name=data.name, source_url=str(data.source_url), source_type_id=data.source_type_id
            )
            obj = await self.repo.create(model)
            return SourceRead.model_validate(obj)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Source already exists") from e

    async def update_source(self, source_id: int, data: SourceUpdate) -> SourceRead:
        obj = await self.repo.get_by_id(source_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Source not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            if isinstance(value, HttpUrl):
                value = str(value)
            setattr(obj, key, value)

        try:
            updated = await self.repo.update(obj)
            return SourceRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Source with these parameters already exists (unique constraint failed)",
            ) from e

    async def delete_source(self, source_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(source_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Source not found")
        return {"deleted": True, "source_id": source_id}
