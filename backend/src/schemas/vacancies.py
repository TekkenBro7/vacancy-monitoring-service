from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.schemas.companies import PaginationInfo, VacancyRead


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class VacancySortField(str, Enum):
    PUBLISHED_AT = "published_at"
    SALARY_FROM = "salary_from"
    SALARY_TO = "salary_to"
    TITLE = "title"
    CREATED_AT = "created_at"


class SalaryRange(str, Enum):
    ANY = "any"
    UP_TO_50K = "up_to_50k"
    FROM_50K_TO_100K = "50k_100k"
    FROM_100K_TO_150K = "100k_150k"
    FROM_150K_TO_200K = "150k_200k"
    FROM_200K = "from_200k"


class ExperienceLevel(str, Enum):
    NO_EXPERIENCE = "no_experience"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"


class VacancyFilters(BaseModel):
    search: str | None = Field(default=None, description="Поиск по названию и описанию")

    source_ids: list[int] | None = Field(default=None, description="ID источников")

    company_ids: list[int] | None = Field(default=None, description="ID компаний")

    city_ids: list[int] | None = Field(default=None, description="ID городов")
    is_remote: bool | None = Field(default=None, description="Только удалённая работа")

    salary_from: int | None = Field(default=None, ge=0, description="Минимальная зарплата")
    salary_to: int | None = Field(default=None, ge=0, description="Максимальная зарплата")
    salary_range: SalaryRange | None = Field(default=None, description="Предустановленный диапазон")
    currency_id: int | None = Field(default=None, description="ID валюты")
    with_salary_only: bool = Field(default=False, description="Только с указанной зарплатой")

    experience: list[str] | None = Field(default=None, description="Требуемый опыт")
    employment: list[str] | None = Field(default=None, description="Тип занятости")
    schedule: list[str] | None = Field(default=None, description="График работы")

    skill_ids: list[int] | None = Field(default=None, description="ID навыков (AND логика)")

    internship: bool | None = Field(default=None, description="Только стажировки")

    is_active: bool | None = Field(default=True, description="Только активные")

    published_after: datetime | None = Field(default=None, description="Опубликовано после")
    published_before: datetime | None = Field(default=None, description="Опубликовано до")

    sort_by: VacancySortField = Field(
        default=VacancySortField.PUBLISHED_AT, description="Поле сортировки"
    )
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Порядок сортировки")


class VacancySearchRequest(BaseModel):
    filters: VacancyFilters = Field(default_factory=VacancyFilters)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class FilterOption(BaseModel):
    id: int | str
    name: str
    count: int = 0


class AvailableFilters(BaseModel):
    sources: list[FilterOption] = Field(default_factory=list)
    companies: list[FilterOption] = Field(default_factory=list)
    cities: list[FilterOption] = Field(default_factory=list)
    currencies: list[FilterOption] = Field(default_factory=list)
    skills: list[FilterOption] = Field(default_factory=list)
    experience: list[FilterOption] = Field(default_factory=list)
    employment: list[FilterOption] = Field(default_factory=list)
    schedule: list[FilterOption] = Field(default_factory=list)

    total_vacancies: int = 0
    with_salary_count: int = 0
    remote_count: int = 0
    internship_count: int = 0


class VacancySearchResponse(BaseModel):
    items: list[VacancyRead]
    pagination: PaginationInfo
    filters: AvailableFilters | None = None
