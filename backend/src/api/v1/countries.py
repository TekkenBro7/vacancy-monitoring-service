from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.locations import CountryCreate, CountryRead, CountryUpdate
from src.services.location_service import CountryService

router = APIRouter()


def get_country_service(db: AsyncSession = Depends(get_async_session)) -> CountryService:
    return CountryService(db)


@router.get("/", response_model=list[CountryRead])
async def list_countries(
    service: CountryService = Depends(get_country_service),
) -> list[CountryRead]:
    return await service.list_countries()


@router.get("/{country_id}/", response_model=CountryRead)
async def get_country(
    country_id: int, service: CountryService = Depends(get_country_service)
) -> CountryRead:
    return await service.get_country(country_id)


@router.post("/", response_model=CountryRead)
async def create_country(
    data: CountryCreate, service: CountryService = Depends(get_country_service)
) -> CountryRead:
    return await service.create_country(data)


@router.patch("/{country_id}/", response_model=CountryRead)
async def update_country(
    country_id: int, data: CountryUpdate, service: CountryService = Depends(get_country_service)
) -> CountryRead:
    return await service.update_country(country_id, data)


@router.delete("/{country_id}/")
async def delete_country(
    country_id: int, service: CountryService = Depends(get_country_service)
) -> dict[str, bool | int]:
    return await service.delete_country(country_id)
