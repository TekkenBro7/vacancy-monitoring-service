from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.parsers.base.parser_result import ParserVacancyResult


@pytest.fixture
def patch_session_maker(db_session: AsyncSession) -> Generator[None, None, None]:
    class FakeSessionContext:
        async def __aenter__(self) -> AsyncSession:
            return db_session

        async def __aexit__(self, *args: object) -> None:
            pass

    with patch(
        "src.core.celery.tasks.import_tasks.async_session_maker",
        return_value=FakeSessionContext(),
    ):
        yield


@pytest.fixture
def mock_import_service() -> Generator[MagicMock, None, None]:
    # Изменено: патчим ImportServiceFactory вместо ParserServiceFactory
    with patch("src.core.celery.tasks.import_tasks.ImportServiceFactory") as mock_factory:
        mock_service = AsyncMock()
        mock_factory.create.return_value = mock_service
        yield mock_service


@pytest.fixture
def sample_vacancy_data() -> dict[str, Any]:
    return {
        "external_id": "12345",
        "vacancy_url": "https://hh.ru/vacancy/12345",
        "title": "Python Developer",
        "description": "Описание вакансии",
        "company_name": "Tech Company",
        "company_external_id": "comp_789",
        "salary_from": 150000,
        "salary_to": 250000,
        "currency": "RUR",
        "city": "Москва",
        "is_remote": True,
        "experience": "1-3 года",
        "employment": "Полная занятость",
        "schedule": "Удалённая работа",
        "internship": False,
        "published_at": "2024-06-15T10:30:00",
        "created_at": "2024-06-14T08:00:00",
    }


@pytest.fixture
def sample_vacancies_batch(sample_vacancy_data: dict[str, Any]) -> list[dict[str, Any]]:
    vacancies = []
    for i in range(5):
        vacancy = sample_vacancy_data.copy()
        vacancy["external_id"] = f"vacancy_{i}"
        vacancy["title"] = f"Developer {i}"
        vacancies.append(vacancy)
    return vacancies


class TestImportVacanciesBatchSuccess:
    @pytest.mark.asyncio
    async def test_imports_single_vacancy(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
        sample_vacancy_data: dict[str, Any],
    ) -> None:
        vacancies_data = [sample_vacancy_data]
        source_name = "HeadHunter"

        await _import_vacancies_batch(vacancies_data, source_name)

        mock_import_service.import_batch.assert_called_once()
        call_args = mock_import_service.import_batch.call_args

        vacancies_arg = call_args[0][0]
        assert len(vacancies_arg) == 1
        assert isinstance(vacancies_arg[0], ParserVacancyResult)
        assert vacancies_arg[0].external_id == "12345"

        source_name_arg = call_args[0][1]
        assert source_name_arg == "HeadHunter"

    @pytest.mark.asyncio
    async def test_imports_multiple_vacancies(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
        sample_vacancies_batch: list[dict[str, Any]],
    ) -> None:
        source_name = "HeadHunter"

        await _import_vacancies_batch(sample_vacancies_batch, source_name)

        mock_import_service.import_batch.assert_called_once()
        call_args = mock_import_service.import_batch.call_args

        vacancies_arg = call_args[0][0]
        assert len(vacancies_arg) == 5

        for vacancy in vacancies_arg:
            assert isinstance(vacancy, ParserVacancyResult)

    @pytest.mark.asyncio
    async def test_imports_empty_batch(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        vacancies_data: list[dict[str, Any]] = []
        source_name = "HeadHunter"

        await _import_vacancies_batch(vacancies_data, source_name)

        mock_import_service.import_batch.assert_called_once()
        call_args = mock_import_service.import_batch.call_args

        vacancies_arg = call_args[0][0]
        assert len(vacancies_arg) == 0

    @pytest.mark.asyncio
    async def test_different_source_names(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
        sample_vacancy_data: dict[str, Any],
    ) -> None:
        source_names = ["HeadHunter", "SuperJob", "LinkedIn"]

        for source_name in source_names:
            await _import_vacancies_batch([sample_vacancy_data], source_name)

        calls = mock_import_service.import_batch.call_args_list

        assert len(calls) == 3

        for i, source_name in enumerate(source_names):
            assert calls[i][0][1] == source_name


class TestImportVacanciesBatchDataConversion:
    @pytest.mark.asyncio
    async def test_converts_datetime_strings(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        vacancy_data = {
            "external_id": "123",
            "title": "Developer",
            "published_at": "2024-06-15T10:30:45",
            "created_at": "2024-06-14T08:00:00",
        }

        await _import_vacancies_batch([vacancy_data], "HeadHunter")

        call_args = mock_import_service.import_batch.call_args
        vacancy = call_args[0][0][0]

        assert isinstance(vacancy.published_at, datetime)
        assert isinstance(vacancy.created_at, datetime)
        assert vacancy.published_at == datetime(2024, 6, 15, 10, 30, 45)

    @pytest.mark.asyncio
    async def test_handles_none_datetime(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        vacancy_data = {
            "external_id": "123",
            "title": "Developer",
            "published_at": None,
            "created_at": None,
        }

        await _import_vacancies_batch([vacancy_data], "HeadHunter")

        call_args = mock_import_service.import_batch.call_args
        vacancy = call_args[0][0][0]

        assert vacancy.published_at is None
        assert vacancy.created_at is None

    @pytest.mark.asyncio
    async def test_preserves_all_fields(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
        sample_vacancy_data: dict[str, Any],
    ) -> None:
        await _import_vacancies_batch([sample_vacancy_data], "HeadHunter")

        call_args = mock_import_service.import_batch.call_args
        vacancy = call_args[0][0][0]

        assert vacancy.external_id == "12345"
        assert vacancy.vacancy_url == "https://hh.ru/vacancy/12345"
        assert vacancy.title == "Python Developer"
        assert vacancy.description == "Описание вакансии"
        assert vacancy.company_name == "Tech Company"
        assert vacancy.company_external_id == "comp_789"
        assert vacancy.salary_from == 150000
        assert vacancy.salary_to == 250000
        assert vacancy.currency == "RUR"
        assert vacancy.city == "Москва"
        assert vacancy.is_remote is True
        assert vacancy.experience == "1-3 года"
        assert vacancy.employment == "Полная занятость"
        assert vacancy.schedule == "Удалённая работа"
        assert vacancy.internship is False

    @pytest.mark.asyncio
    async def test_minimal_vacancy_data(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        vacancy_data = {
            "external_id": "minimal_123",
            "title": "Junior Developer",
        }

        await _import_vacancies_batch([vacancy_data], "HeadHunter")

        call_args = mock_import_service.import_batch.call_args
        vacancy = call_args[0][0][0]

        assert vacancy.external_id == "minimal_123"
        assert vacancy.title == "Junior Developer"
        assert vacancy.salary_from is None
        assert vacancy.company_name is None


class TestImportVacanciesBatchErrors:
    @pytest.mark.asyncio
    async def test_invalid_vacancy_data_raises(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        invalid_data = {
            "external_id": "123",
            # "title" missing
        }

        with patch("src.core.celery.tasks.import_tasks.logger") as mock_logger:
            await _import_vacancies_batch([invalid_data], "HeadHunter")

            mock_logger.exception.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_datetime_format_raises(
        self,
        patch_session_maker: None,
        mock_import_service: MagicMock,
    ) -> None:
        vacancy_data = {
            "external_id": "123",
            "title": "Developer",
            "published_at": "invalid-date-format",
        }

        with patch("src.core.celery.tasks.import_tasks.logger") as mock_logger:
            await _import_vacancies_batch([vacancy_data], "HeadHunter")

            mock_logger.exception.assert_called_once()
