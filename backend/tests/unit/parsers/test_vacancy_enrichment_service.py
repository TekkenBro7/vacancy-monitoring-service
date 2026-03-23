from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.companies import Vacancy
from src.models.skills import Skill
from src.models.sources import Source
from src.parsers.hh_ru.vacancy_enrichment_service import VacancyEnrichmentService


@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_skill_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.get_or_create_many = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_parser() -> AsyncMock:
    parser = AsyncMock()
    parser.get_vacancy = AsyncMock(return_value=None)
    return parser


@pytest.fixture
def service(
    mock_db_session: AsyncMock,
    mock_skill_repository: AsyncMock,
    mock_parser: AsyncMock,
) -> VacancyEnrichmentService:
    svc = VacancyEnrichmentService(mock_db_session)
    svc.skill_repository = mock_skill_repository
    svc.parser = mock_parser
    return svc


@pytest.fixture
def hh_source() -> MagicMock:
    source = MagicMock(spec=Source)
    source.name = "HeadHunter"
    return source


@pytest.fixture
def other_source() -> MagicMock:
    source = MagicMock(spec=Source)
    source.name = "SuperJob"
    return source


@pytest.fixture
def vacancy_without_description(hh_source: MagicMock) -> MagicMock:
    vacancy = MagicMock(spec=Vacancy)
    vacancy.id = 1
    vacancy.external_id = "12345"
    vacancy.source = hh_source
    vacancy.description = None
    vacancy.skills = []
    vacancy.last_seen_at = datetime.now(UTC)
    vacancy.created_at = datetime.now(UTC)
    vacancy.last_enriched_at = None
    vacancy.experience = None
    vacancy.schedule = None
    vacancy.employment = None
    vacancy.salary_from = None
    vacancy.salary_to = None
    return vacancy


@pytest.fixture
def vacancy_without_skills(hh_source: MagicMock) -> MagicMock:
    vacancy = MagicMock(spec=Vacancy)
    vacancy.id = 2
    vacancy.external_id = "67890"
    vacancy.source = hh_source
    vacancy.description = "Some description"
    vacancy.skills = []
    vacancy.last_seen_at = datetime.now(UTC)
    vacancy.created_at = datetime.now(UTC)
    vacancy.last_enriched_at = None
    vacancy.experience = None
    vacancy.schedule = None
    vacancy.employment = None
    vacancy.salary_from = None
    vacancy.salary_to = None
    return vacancy


@pytest.fixture
def fully_enriched_vacancy(hh_source: MagicMock) -> MagicMock:
    vacancy = MagicMock(spec=Vacancy)
    vacancy.id = 3
    vacancy.external_id = "11111"
    vacancy.source = hh_source
    vacancy.description = "Full description"
    vacancy.skills = [MagicMock(spec=Skill)]
    vacancy.last_seen_at = datetime.now(UTC)
    vacancy.created_at = datetime.now(UTC)
    vacancy.last_enriched_at = datetime.now(UTC)
    vacancy.experience = "1-3 года"
    vacancy.schedule = "Полный день"
    vacancy.employment = "Полная занятость"
    vacancy.salary_from = 100000
    vacancy.salary_to = 200000
    return vacancy


@pytest.fixture
def old_vacancy(hh_source: MagicMock) -> MagicMock:
    vacancy = MagicMock(spec=Vacancy)
    vacancy.id = 4
    vacancy.external_id = "22222"
    vacancy.source = hh_source
    vacancy.description = "Description"
    vacancy.skills = [MagicMock(spec=Skill)]
    vacancy.last_seen_at = datetime.now(UTC) - timedelta(days=10)
    vacancy.created_at = datetime.now(UTC) - timedelta(days=10)
    vacancy.last_enriched_at = None
    vacancy.experience = None
    vacancy.schedule = None
    vacancy.employment = None
    vacancy.salary_from = None
    vacancy.salary_to = None
    return vacancy


@pytest.fixture
def sample_enriched_data() -> dict[str, Any]:
    return {
        "description": "<p>Detailed job description</p>",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience": "1-3 года",
        "schedule": "Удалённая работа",
        "employment": "Полная занятость",
        "salary_from": 150000,
        "salary_to": 250000,
        "work_format": "Удалённая работа",
    }


@pytest.fixture
def sample_api_response() -> dict[str, Any]:
    return {
        "description": "<p>Detailed job description</p>",
        "key_skills": [
            {"name": "Python"},
            {"name": "FastAPI"},
            {"name": "PostgreSQL"},
        ],
        "experience": {"id": "between1And3", "name": "1-3 года"},
        "schedule": {"id": "remote", "name": "Удалённая работа"},
        "employment": {"id": "full", "name": "Полная занятость"},
        "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
        "work_format": [{"id": "remote", "name": "Удалённая работа"}],
    }


class TestShouldEnrich:
    def test_returns_false_when_no_source(self, service: VacancyEnrichmentService) -> None:
        vacancy = MagicMock(spec=Vacancy)
        vacancy.source = None

        result, reason = service._should_enrich(vacancy)

        assert result is False
        assert reason == "No source"

    def test_returns_false_when_not_hh_source(
        self, service: VacancyEnrichmentService, other_source: MagicMock
    ) -> None:
        vacancy = MagicMock(spec=Vacancy)
        vacancy.source = other_source

        result, reason = service._should_enrich(vacancy)

        assert result is False
        assert "SuperJob" in reason

    def test_returns_false_when_no_external_id(
        self, service: VacancyEnrichmentService, hh_source: MagicMock
    ) -> None:
        vacancy = MagicMock(spec=Vacancy)
        vacancy.source = hh_source
        vacancy.external_id = None

        result, reason = service._should_enrich(vacancy)

        assert result is False
        assert reason == "No external_id"

    def test_returns_true_when_no_description(
        self, service: VacancyEnrichmentService, vacancy_without_description: MagicMock
    ) -> None:
        result, reason = service._should_enrich(vacancy_without_description)

        assert result is True
        assert reason == "No description"

    def test_returns_true_when_no_skills(
        self, service: VacancyEnrichmentService, vacancy_without_skills: MagicMock
    ) -> None:
        result, reason = service._should_enrich(vacancy_without_skills)

        assert result is True
        assert reason == "No skills"

    def test_returns_true_when_old_vacancy(
        self, service: VacancyEnrichmentService, old_vacancy: MagicMock
    ) -> None:
        result, reason = service._should_enrich(old_vacancy)

        assert result is True
        assert "7 days" in reason

    def test_returns_false_when_fully_enriched(
        self, service: VacancyEnrichmentService, fully_enriched_vacancy: MagicMock
    ) -> None:
        result, reason = service._should_enrich(fully_enriched_vacancy)

        assert result is False
        assert reason == "Already enriched and recent"

    def test_returns_true_when_empty_description(
        self, service: VacancyEnrichmentService, hh_source: MagicMock
    ) -> None:
        vacancy = MagicMock(spec=Vacancy)
        vacancy.source = hh_source
        vacancy.external_id = "123"
        vacancy.description = "   "
        vacancy.skills = [MagicMock(spec=Skill)]
        vacancy.last_seen_at = datetime.now(UTC)

        result, reason = service._should_enrich(vacancy)

        assert result is True
        assert reason == "No description"


class TestEnrichVacancyIfNeeded:
    @pytest.mark.asyncio
    async def test_skips_when_not_needed(
        self,
        service: VacancyEnrichmentService,
        fully_enriched_vacancy: MagicMock,
        mock_parser: AsyncMock,
    ) -> None:
        result = await service.enrich_vacancy_if_needed(fully_enriched_vacancy)

        assert result == fully_enriched_vacancy
        mock_parser.get_vacancy.assert_not_called()

    @pytest.mark.asyncio
    async def test_enriches_when_no_description(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_description: MagicMock,
        sample_enriched_data: dict[str, Any],
        mock_skill_repository: AsyncMock,
    ) -> None:
        with patch.object(service, "enrich_vacancy_data", new_callable=AsyncMock) as mock_enrich:
            mock_enrich.return_value = sample_enriched_data
            mock_skill_repository.get_or_create_many.return_value = []

            result = await service.enrich_vacancy_if_needed(vacancy_without_description)

        mock_enrich.assert_called_once_with(vacancy_without_description.external_id)
        assert result.last_enriched_at is not None

    @pytest.mark.asyncio
    async def test_updates_vacancy_fields(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_description: MagicMock,
        sample_enriched_data: dict[str, Any],
        mock_skill_repository: AsyncMock,
    ) -> None:
        with patch.object(service, "enrich_vacancy_data", new_callable=AsyncMock) as mock_enrich:
            mock_enrich.return_value = sample_enriched_data
            mock_skill_repository.get_or_create_many.return_value = []

            await service.enrich_vacancy_if_needed(vacancy_without_description)

        assert vacancy_without_description.description == sample_enriched_data["description"]

    @pytest.mark.asyncio
    async def test_handles_enrichment_failure(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_description: MagicMock,
    ) -> None:
        with patch.object(service, "enrich_vacancy_data", new_callable=AsyncMock) as mock_enrich:
            mock_enrich.return_value = None

            result = await service.enrich_vacancy_if_needed(vacancy_without_description)

        assert result == vacancy_without_description
        assert vacancy_without_description.last_enriched_at is None


class TestEnrichVacancyData:
    @pytest.mark.asyncio
    async def test_returns_enriched_data(
        self,
        service: VacancyEnrichmentService,
        sample_api_response: dict[str, Any],
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = sample_api_response

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["description"] == "<p>Detailed job description</p>"
        assert result["skills"] == ["Python", "FastAPI", "PostgreSQL"]
        assert result["experience"] == "1-3 года"
        assert result["salary_from"] == 150000
        assert result["salary_to"] == 250000

    @pytest.mark.asyncio
    async def test_returns_none_when_api_fails(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = None

        result = await service.enrich_vacancy_data("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_missing_salary(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = {
            "description": "Test",
            "key_skills": [],
        }

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["salary_from"] is None
        assert result["salary_to"] is None

    @pytest.mark.asyncio
    async def test_handles_empty_skills(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = {
            "description": "Test",
            "key_skills": [],
        }

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["skills"] == []

    @pytest.mark.asyncio
    async def test_filters_skills_without_name(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = {
            "description": "Test",
            "key_skills": [
                {"name": "Python"},
                {"name": None},
                {},
                {"name": "FastAPI"},
            ],
        }

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["skills"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_handles_missing_work_format(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = {
            "description": "Test",
            "key_skills": [],
        }

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["work_format"] is None

    @pytest.mark.asyncio
    async def test_extracts_work_format(
        self,
        service: VacancyEnrichmentService,
        mock_parser: AsyncMock,
    ) -> None:
        mock_parser.get_vacancy.return_value = {
            "description": "Test",
            "key_skills": [],
            "work_format": [{"id": "remote", "name": "Удалённая работа"}],
        }

        result = await service.enrich_vacancy_data("12345")

        assert result is not None
        assert result["work_format"] == "Удалённая работа"


class TestUpdateVacancy:
    @pytest.mark.asyncio
    async def test_updates_description(
        self, service: VacancyEnrichmentService, vacancy_without_description: MagicMock
    ) -> None:
        data: dict[str, Any] = {"description": "New description"}

        await service._update_vacancy(vacancy_without_description, data)

        assert vacancy_without_description.description == "New description"

    @pytest.mark.asyncio
    async def test_creates_and_attaches_skills(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_skills: MagicMock,
        mock_skill_repository: AsyncMock,
    ) -> None:
        skill1 = MagicMock(spec=Skill)
        skill1.name = "Python"
        skill2 = MagicMock(spec=Skill)
        skill2.name = "FastAPI"
        mock_skill_repository.get_or_create_many.return_value = [skill1, skill2]
        vacancy_without_skills.skills = []

        data: dict[str, Any] = {"skills": ["Python", "FastAPI"]}

        await service._update_vacancy(vacancy_without_skills, data)

        mock_skill_repository.get_or_create_many.assert_called_once_with(["Python", "FastAPI"])

    @pytest.mark.asyncio
    async def test_does_not_overwrite_existing_experience(
        self, service: VacancyEnrichmentService
    ) -> None:
        vacancy = MagicMock(spec=Vacancy)
        vacancy.skills = []
        vacancy.experience = "3-5 лет"

        data: dict[str, Any] = {"experience": "1-3 года"}

        await service._update_vacancy(vacancy, data)

        assert vacancy.experience == "3-5 лет"

    @pytest.mark.asyncio
    async def test_updates_missing_experience(
        self, service: VacancyEnrichmentService, vacancy_without_description: MagicMock
    ) -> None:
        data: dict[str, Any] = {"experience": "1-3 года"}

        await service._update_vacancy(vacancy_without_description, data)

        assert vacancy_without_description.experience == "1-3 года"

    @pytest.mark.asyncio
    async def test_updates_all_missing_fields(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_description: MagicMock,
        mock_skill_repository: AsyncMock,
    ) -> None:
        mock_skill_repository.get_or_create_many.return_value = []
        data: dict[str, Any] = {
            "description": "New desc",
            "skills": [],
            "experience": "1-3 года",
            "schedule": "Удалённая работа",
            "employment": "Полная занятость",
            "salary_from": 100000,
            "salary_to": 200000,
        }

        await service._update_vacancy(vacancy_without_description, data)

        assert vacancy_without_description.description == "New desc"
        assert vacancy_without_description.experience == "1-3 года"
        assert vacancy_without_description.schedule == "Удалённая работа"
        assert vacancy_without_description.employment == "Полная занятость"
        assert vacancy_without_description.salary_from == 100000
        assert vacancy_without_description.salary_to == 200000


class TestCreateAndAttachSkills:
    @pytest.mark.asyncio
    async def test_attaches_new_skills(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_skills: MagicMock,
        mock_skill_repository: AsyncMock,
    ) -> None:
        skill1 = MagicMock(spec=Skill)
        skill1.name = "Python"
        skill2 = MagicMock(spec=Skill)
        skill2.name = "FastAPI"
        mock_skill_repository.get_or_create_many.return_value = [skill1, skill2]
        vacancy_without_skills.skills = []

        await service._create_and_attach_skills(vacancy_without_skills, ["Python", "FastAPI"])

        assert skill1 in vacancy_without_skills.skills
        assert skill2 in vacancy_without_skills.skills

    @pytest.mark.asyncio
    async def test_does_not_duplicate_skills(
        self,
        service: VacancyEnrichmentService,
        mock_skill_repository: AsyncMock,
    ) -> None:
        existing_skill = MagicMock(spec=Skill)
        existing_skill.name = "Python"

        vacancy = MagicMock(spec=Vacancy)
        vacancy.skills = [existing_skill]

        mock_skill_repository.get_or_create_many.return_value = [existing_skill]

        await service._create_and_attach_skills(vacancy, ["Python"])

        assert vacancy.skills.count(existing_skill) == 1

    @pytest.mark.asyncio
    async def test_handles_empty_skill_list(
        self,
        service: VacancyEnrichmentService,
        vacancy_without_skills: MagicMock,
        mock_skill_repository: AsyncMock,
    ) -> None:
        mock_skill_repository.get_or_create_many.return_value = []

        await service._create_and_attach_skills(vacancy_without_skills, [])

        mock_skill_repository.get_or_create_many.assert_called_once_with([])
