from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.sources import SourceTypeCreate, SourceTypeRead, SourceTypeUpdate
from src.services.source_service import SourceTypeService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> SourceTypeService:
    return SourceTypeService(db)


@router.get("/", response_model=list[SourceTypeRead])
async def list_source_types(
    service: SourceTypeService = Depends(get_service),
) -> list[SourceTypeRead]:
    return await service.list_source_types()


@router.get("/{type_id}/", response_model=SourceTypeRead)
async def get_source_type(
    type_id: int, service: SourceTypeService = Depends(get_service)
) -> SourceTypeRead:
    return await service.get_source_type(type_id)


@router.post("/", response_model=SourceTypeRead)
async def create_source_type(
    data: SourceTypeCreate, service: SourceTypeService = Depends(get_service)
) -> SourceTypeRead:
    return await service.create_source_type(data)


@router.patch("/{type_id}/", response_model=SourceTypeRead)
async def update_source_type(
    type_id: int, data: SourceTypeUpdate, service: SourceTypeService = Depends(get_service)
) -> SourceTypeRead:
    return await service.update_source_type(type_id, data)


@router.delete("/{type_id}/")
async def delete_source_type(
    type_id: int, service: SourceTypeService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_source_type(type_id)
