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


class CurrencyRead(BaseModel):
    id: int
    name: str
    symbol: str | None

    model_config = {"from_attributes": True}


class CityRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SourceRead(BaseModel):
    id: int
    name: str
    source_url: str
    source_type_id: int

    model_config = {"from_attributes": True}


class SkillRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class VacancyRead(BaseModel):
    id: int
    title: str
    description: str | None
    salary_from: int | None
    salary_to: int | None
    external_id: str
    experience: str | None
    education: str | None
    employment: str | None
    schedule: str | None
    internship: bool | None
    vacancy_url: str | None
    is_remote: bool | None
    is_active: bool | None
    address: str | None
    created_at: datetime | None
    created_at_source: datetime | None
    updated_at: datetime | None
    published_at: datetime | None
    last_seen_at: datetime | None
    last_enriched_at: datetime | None
    fingerprint: str

    currency: CurrencyRead | None = None
    company: CompanyRead | None = None
    source: SourceRead | None = None
    location: CityRead | None = None
    skills: list[SkillRead] = []

    model_config = {"from_attributes": True}


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


class VacancyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    currency_id: int | None = None
    vacancy_url: HttpUrl | None = None
    is_remote: bool | None = None
    is_active: bool | None = None
    experience: str | None = None
    education: str | None = None
    employment: str | None = None
    schedule: str | None = None
    internship: bool | None = None
    address: str | None = None
    skill_ids: list[int] | None = None


class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse[T](BaseModel):
    items: list[T]
    pagination: PaginationInfo
