from datetime import datetime

from pydantic import BaseModel, HttpUrl


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    website: HttpUrl | None = None


class CompanyRead(BaseModel):
    id: int
    name: str
    description: str | None
    website: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    website: HttpUrl | None = None


class VacancyCreate(BaseModel):
    title: str
    description: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    currency_id: int | None = None
    company_id: int
    source_id: int
    location_id: int | None = None
    vacancy_url: HttpUrl | None = None
    is_remote: bool | None = False
    is_active: bool | None = True
    published_at: datetime | None = None


class VacancyRead(BaseModel):
    id: int
    title: str
    description: str | None
    salary_from: int | None
    salary_to: int | None
    currency_id: int | None
    company_id: int
    source_id: int
    location_id: int | None
    vacancy_url: str | None
    is_remote: bool | None
    is_active: bool | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VacancyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    currency_id: int | None = None
    company_id: int | None = None
    source_id: int | None = None
    location_id: int | None = None
    vacancy_url: HttpUrl | None = None
    is_remote: bool | None = None
    is_active: bool | None = None
    published_at: datetime | None = None
