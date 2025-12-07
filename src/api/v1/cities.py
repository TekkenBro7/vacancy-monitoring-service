from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.locations import CityCreate, CityRead, CityUpdate
from src.services.location_service import CityService

router = APIRouter()


def get_city_service(db: AsyncSession = Depends(get_async_session)) -> CityService:
    return CityService(db)


@router.get("/", response_model=list[CityRead])
async def list_cities(service: CityService = Depends(get_city_service)) -> list[CityRead]:
    return await service.list_cities()


@router.get("/{city_id}", response_model=CityRead)
async def get_city(city_id: int, service: CityService = Depends(get_city_service)) -> CityRead:
    return await service.get_city(city_id)


@router.post("/", response_model=CityRead)
async def create_city(
    data: CityCreate, service: CityService = Depends(get_city_service)
) -> CityRead:
    return await service.create_city(data)


@router.patch("/{city_id}", response_model=CityRead)
async def update_city(
    city_id: int, data: CityUpdate, service: CityService = Depends(get_city_service)
) -> CityRead:
    return await service.update_city(city_id, data)


@router.delete("/{city_id}")
async def delete_city(
    city_id: int, service: CityService = Depends(get_city_service)
) -> dict[str, bool | int]:
    return await service.delete_city(city_id)
