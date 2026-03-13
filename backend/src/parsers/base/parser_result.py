from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParserVacancyResult:
    external_id: str
    title: str
    description: str | None

    company_external_id: str | None
    company_name: str | None

    salary_from: int | None
    salary_to: int | None
    currency: str | None

    city: str | None

    vacancy_url: str | None

    experience: str | None
    employment: str | None
    schedule: str | None

    published_at: datetime | None
    created_at: datetime | None

    is_remote: bool = False
