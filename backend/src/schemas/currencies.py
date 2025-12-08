from datetime import datetime

from pydantic import BaseModel


class CurrencyCreate(BaseModel):
    name: str
    symbol: str | None = None


class CurrencyRead(BaseModel):
    id: int
    name: str
    symbol: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CurrencyUpdate(BaseModel):
    name: str | None = None
    symbol: str | None = None
