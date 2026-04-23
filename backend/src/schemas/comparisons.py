from datetime import datetime

from pydantic import BaseModel, Field


class ComparisonCreate(BaseModel):
    name: str


class ComparisonUpdate(BaseModel):
    name: str | None = None


class VacancyInComparison(BaseModel):
    id: int
    title: str
    description: str | None = None

    salary_from: int | None = None
    salary_to: int | None = None
    currency_code: str | None = None

    company_id: int | None = None
    company_name: str | None = None

    city_name: str | None = None
    address: str | None = None
    is_remote: bool | None = None

    experience: str | None = None
    education: str | None = None
    employment: str | None = None
    schedule: str | None = None
    internship: bool | None = None

    skills: list[str] = Field(default_factory=list)

    vacancy_url: str | None = None
    source_name: str | None = None
    published_at: datetime | None = None


class ComparisonRead(BaseModel):
    id: int
    name: str
    user_id: int
    vacancy_ids: list[int] = Field(default_factory=list)
    vacancies_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComparisonDetailRead(BaseModel):
    id: int
    name: str
    user_id: int
    vacancies: list[VacancyInComparison] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ComparisonAnalysisRead(BaseModel):
    id: int
    name: str
    user_id: int
    vacancies: list[VacancyInComparison] = Field(default_factory=list)

    ai_analysis: str = Field(description="Текстовый анализ от AI в формате Markdown")

    created_at: datetime
    updated_at: datetime


class AddVacanciesRequest(BaseModel):
    vacancy_ids: list[int]
