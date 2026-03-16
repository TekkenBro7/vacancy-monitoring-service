from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class ParserVacancyResult:
    # external
    external_id: str
    vacancy_url: str | None = None

    # title / description
    title: str
    description: str | None = None

    # company
    company_name: str | None = None
    company_external_id: str | None = None

    # salary
    salary_from: int | None = None
    salary_to: int | None = None
    currency: str | None = None

    # location
    city: str | None = None
    is_remote: bool = False

    # job info
    experience: str | None = None
    employment: str | None = None
    schedule: str | None = None
    internship: str | None = None

    # timestamps
    published_at: datetime | None = None
    created_at: datetime | None = None
