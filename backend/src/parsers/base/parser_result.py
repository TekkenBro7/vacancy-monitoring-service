from dataclasses import asdict, dataclass
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
    internship: bool | None = None

    # timestamps
    published_at: datetime | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        data = asdict(self)

        if self.published_at:
            data["published_at"] = self.published_at.isoformat()

        if self.created_at:
            data["created_at"] = self.created_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ParserVacancyResult":
        data = data.copy()

        if data.get("published_at"):
            data["published_at"] = datetime.fromisoformat(data["published_at"])

        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)
