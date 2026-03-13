from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.currency_repository import CurrencyRepository
from src.models.currencies import Currency
from src.schemas.currencies import (
    CurrencyCreate,
    CurrencyRead,
    CurrencyUpdate,
)


class CurrencyService:
    def __init__(self, db: AsyncSession):
        self.repo = CurrencyRepository(Currency, db)

    async def list_currencies(self) -> list[CurrencyRead]:
        items = await self.repo.list()
        return [CurrencyRead.model_validate(obj) for obj in items]

    async def get_currency(self, currency_id: int) -> CurrencyRead:
        currency = await self.repo.get_by_id(currency_id)
        if not currency:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Currency not found")

        return CurrencyRead.model_validate(currency)

    async def create_currency(self, data: CurrencyCreate) -> CurrencyRead:
        try:
            currency_model = Currency(name=data.name, symbol=data.symbol)
            currency = await self.repo.create(currency_model)

            return CurrencyRead.model_validate(currency)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Currency with this name already exists",
            ) from e

    async def update_currency(self, currency_id: int, data: CurrencyUpdate) -> CurrencyRead:
        currency = await self.repo.get_by_id(currency_id)
        if not currency:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Currency not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(currency, key, value)

        try:
            updated = await self.repo.update(currency)
            return CurrencyRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Currency update conflict",
            ) from e

    async def delete_currency(self, currency_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(currency_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Currency not found")

        return {"deleted": True, "currency_id": currency_id}
