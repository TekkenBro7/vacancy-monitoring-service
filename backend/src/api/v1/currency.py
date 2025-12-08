from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.currencies import CurrencyCreate, CurrencyRead, CurrencyUpdate
from src.services.currency_service import CurrencyService

router = APIRouter()


def get_currency_service(
    db: AsyncSession = Depends(get_async_session),
) -> CurrencyService:
    return CurrencyService(db)


@router.get("/", response_model=list[CurrencyRead])
async def list_currencies(
    service: CurrencyService = Depends(get_currency_service),
) -> list[CurrencyRead]:
    return await service.list_currencies()


@router.get("/{currency_id}", response_model=CurrencyRead)
async def get_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service),
) -> CurrencyRead:
    return await service.get_currency(currency_id)


@router.post("/", response_model=CurrencyRead)
async def create_currency(
    data: CurrencyCreate,
    service: CurrencyService = Depends(get_currency_service),
) -> CurrencyRead:
    return await service.create_currency(data)


@router.patch("/{currency_id}", response_model=CurrencyRead)
async def update_currency(
    currency_id: int,
    data: CurrencyUpdate,
    service: CurrencyService = Depends(get_currency_service),
) -> CurrencyRead:
    return await service.update_currency(currency_id, data)


@router.delete("/{currency_id}")
async def delete_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service),
) -> dict[str, bool | int]:
    return await service.delete_currency(currency_id)
