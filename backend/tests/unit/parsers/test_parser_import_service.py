from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.companies import Vacancy
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.services.parser_import_service import ParserImportService


@pytest.fixture
def mock_vacancy_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_cache_service() -> AsyncMock:
    cache = AsyncMock()
    cache.get_source_id.return_value = 1
    cache.get_company_id.return_value = 10
    cache.get_currency_id.return_value = 100
    cache.get_city_id.return_value = 1000
    return cache


@pytest.fixture
def service(mock_vacancy_repo: AsyncMock, mock_cache_service: AsyncMock) -> ParserImportService:
    return ParserImportService(mock_vacancy_repo, mock_cache_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="12345",
        title="Python Developer",
        description="Great job",
        company_name="Tech Company",
        salary_from=150000,
        salary_to=250000,
        currency="RUR",
        city="Москва",
        experience="1-3 года",
        employment="Полная занятость",
        schedule="Удалённая работа",
        is_remote=True,
        vacancy_url="https://hh.ru/vacancy/12345",
        published_at=datetime(2024, 6, 15),
        created_at=datetime(2024, 6, 14),
        internship=False,
    )


class TestImportBatch:
    @pytest.mark.asyncio
    async def test_imports_all_vacancies_in_batch(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
    ) -> None:
        vacancies = [sample_vacancy, sample_vacancy, sample_vacancy]
        mock_vacancy_repo.get_by_source_and_external_id.return_value = None
        mock_vacancy_repo.get_by_fingerprint.return_value = None

        await service.import_batch(vacancies, "HeadHunter")

        assert mock_vacancy_repo.create.call_count == 3

    @pytest.mark.asyncio
    async def test_imports_empty_batch(
        self,
        service: ParserImportService,
        mock_vacancy_repo: AsyncMock,
    ) -> None:
        await service.import_batch([], "HeadHunter")

        mock_vacancy_repo.create.assert_not_called()


class TestImportVacancy:
    @pytest.mark.asyncio
    async def test_creates_new_vacancy(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
        mock_cache_service: AsyncMock,
    ) -> None:
        mock_vacancy_repo.get_by_source_and_external_id.return_value = None
        mock_vacancy_repo.get_by_fingerprint.return_value = None

        await service.import_vacancy(sample_vacancy, "HeadHunter")

        mock_vacancy_repo.create.assert_called_once()
        created_vacancy = mock_vacancy_repo.create.call_args[0][0]
        assert created_vacancy.title == "Python Developer"
        assert created_vacancy.external_id == "12345"
        assert created_vacancy.is_active is True

    @pytest.mark.asyncio
    async def test_skips_when_source_not_found(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
        mock_cache_service: AsyncMock,
    ) -> None:
        mock_cache_service.get_source_id.return_value = None

        await service.import_vacancy(sample_vacancy, "UnknownSource")

        mock_vacancy_repo.create.assert_not_called()
        mock_vacancy_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_last_seen_for_existing_active_vacancy(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
    ) -> None:
        existing = MagicMock(spec=Vacancy)
        existing.is_active = True
        existing.last_seen_at = datetime(2024, 1, 1, tzinfo=UTC)
        mock_vacancy_repo.get_by_source_and_external_id.return_value = existing

        await service.import_vacancy(sample_vacancy, "HeadHunter")

        mock_vacancy_repo.update.assert_called_once_with(existing)
        assert existing.last_seen_at > datetime(2024, 1, 1, tzinfo=UTC)
        mock_vacancy_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_reactivates_inactive_vacancy(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
    ) -> None:
        existing = MagicMock(spec=Vacancy)
        existing.is_active = False
        mock_vacancy_repo.get_by_source_and_external_id.return_value = existing

        await service.import_vacancy(sample_vacancy, "HeadHunter")

        assert existing.is_active is True
        assert existing.title == "Python Developer"
        mock_vacancy_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_duplicate_by_fingerprint(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
    ) -> None:
        duplicate = MagicMock(spec=Vacancy)
        duplicate.last_seen_at = datetime(2024, 1, 1, tzinfo=UTC)
        mock_vacancy_repo.get_by_source_and_external_id.return_value = None
        mock_vacancy_repo.get_by_fingerprint.return_value = duplicate

        await service.import_vacancy(sample_vacancy, "HeadHunter")

        mock_vacancy_repo.update.assert_called_once_with(duplicate)
        assert duplicate.last_seen_at > datetime(2024, 1, 1, tzinfo=UTC)
        mock_vacancy_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_all_ids_from_cache(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
        mock_vacancy_repo: AsyncMock,
        mock_cache_service: AsyncMock,
    ) -> None:
        mock_vacancy_repo.get_by_source_and_external_id.return_value = None
        mock_vacancy_repo.get_by_fingerprint.return_value = None

        await service.import_vacancy(sample_vacancy, "HeadHunter")

        mock_cache_service.get_source_id.assert_called_once_with("HeadHunter")
        mock_cache_service.get_company_id.assert_called_once_with("Tech Company")
        mock_cache_service.get_currency_id.assert_called_once_with("RUR")
        mock_cache_service.get_city_id.assert_called_once_with("Москва")

    @pytest.mark.asyncio
    async def test_creates_vacancy_with_none_optional_ids(
        self,
        service: ParserImportService,
        mock_vacancy_repo: AsyncMock,
        mock_cache_service: AsyncMock,
    ) -> None:
        vacancy = ParserVacancyResult(
            external_id="99999",
            title="Junior Dev",
        )
        mock_cache_service.get_currency_id.return_value = None
        mock_cache_service.get_city_id.return_value = None
        mock_vacancy_repo.get_by_source_and_external_id.return_value = None
        mock_vacancy_repo.get_by_fingerprint.return_value = None

        await service.import_vacancy(vacancy, "HeadHunter")

        created = mock_vacancy_repo.create.call_args[0][0]
        assert created.currency_id is None
        assert created.location_id is None


class TestApplyVacancyData:
    def test_applies_all_fields(
        self,
        service: ParserImportService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        model = MagicMock(spec=Vacancy)

        service._apply_vacancy_data(
            model=model,
            vacancy=sample_vacancy,
            company_id=10,
            source_id=1,
            currency_id=100,
            city_id=1000,
            fingerprint="abc123",
        )

        assert model.title == "Python Developer"
        assert model.description == "Great job"
        assert model.salary_from == 150000
        assert model.salary_to == 250000
        assert model.company_id == 10
        assert model.source_id == 1
        assert model.currency_id == 100
        assert model.location_id == 1000
        assert model.fingerprint == "abc123"
        assert model.is_remote is True
