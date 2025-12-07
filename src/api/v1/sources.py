from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.sources import SourceCreate, SourceRead, SourceUpdate
from src.services.source_service import SourceService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> SourceService:
    return SourceService(db)


@router.get("/", response_model=list[SourceRead])
async def list_sources(service: SourceService = Depends(get_service)) -> list[SourceRead]:
    return await service.list_sources()


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(source_id: int, service: SourceService = Depends(get_service)) -> SourceRead:
    return await service.get_source(source_id)


@router.post("/", response_model=SourceRead)
async def create_source(
    data: SourceCreate, service: SourceService = Depends(get_service)
) -> SourceRead:
    return await service.create_source(data)


@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: int, data: SourceUpdate, service: SourceService = Depends(get_service)
) -> SourceRead:
    return await service.update_source(source_id, data)


@router.delete("/{source_id}")
async def delete_source(
    source_id: int, service: SourceService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_source(source_id)
