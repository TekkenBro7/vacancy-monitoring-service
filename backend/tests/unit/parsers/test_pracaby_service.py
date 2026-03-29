from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.praca_by.praca_service import PracaByVacancyService
from src.parsers.services.parser_import_service import ParserImportService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock(spec=ParserImportService)


@pytest.fixture
def service(mock_import_service: MagicMock) -> PracaByVacancyService:
    return PracaByVacancyService(mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="12345",
        title="Python Developer",
        company_name="Tech Company",
        company_external_id="999",
        salary_from=2000,
        salary_to=3500,
        currency="BYN",
        city="Минск",
        address="ул. Тестовая, 123",
        experience="от 1 года",
        education="Высшее",
        employment="Полная",
        schedule="Полный день",
        is_remote=False,
        internship=False,
        vacancy_url="https://praca.by/vacancy/12345/",
    )


class TestImportDate:
    @pytest.mark.asyncio
    async def test_imports_vacancies_for_date(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        mock_client = AsyncMock()
        target_date = datetime(2024, 6, 15)

        async def mock_stream(*args, **kwargs):
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            result = await service._import_date(mock_client, target_date)

        assert result == 1
        mock_task.delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_imports_multiple_pages(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        mock_client = AsyncMock()
        target_date = datetime(2024, 6, 15)

        async def mock_stream(*args, **kwargs):
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            result = await service._import_date(mock_client, target_date)

        assert result == 3
        assert mock_task.delay.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_vacancies(
        self,
        service: PracaByVacancyService,
    ) -> None:
        mock_client = AsyncMock()
        target_date = datetime(2024, 6, 15)

        async def mock_stream(*args, **kwargs):
            return
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            result = await service._import_date(mock_client, target_date)

        assert result == 0
        mock_task.delay.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_correct_payload(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        mock_client = AsyncMock()
        target_date = datetime(2024, 6, 15)

        async def mock_stream(*args, **kwargs):
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            await service._import_date(mock_client, target_date)

        call_args = mock_task.delay.call_args
        payload = call_args[0][0]
        source_name = call_args[0][1]

        assert len(payload) == 1
        assert payload[0]["external_id"] == "12345"
        assert payload[0]["title"] == "Python Developer"
        assert source_name == "PracaBy"


class TestRun:
    @pytest.mark.asyncio
    async def test_runs_for_single_day(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 16)

        async def mock_stream(*args, **kwargs):
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            await service.run(None, from_date, to_date)

        mock_task.delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_runs_for_multiple_days(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 18)

        async def mock_stream(*args, **kwargs):
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task,
        ):
            await service.run(None, from_date, to_date)

        assert mock_task.delay.call_count == 3

    @pytest.mark.asyncio
    async def test_handles_empty_date_range(
        self,
        service: PracaByVacancyService,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 15)

        with patch("src.parsers.praca_by.praca_service.import_vacancies_batch") as mock_task:
            await service.run(None, from_date, to_date)

        mock_task.delay.assert_not_called()

    @pytest.mark.asyncio
    async def test_processes_days_sequentially(
        self,
        service: PracaByVacancyService,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 17)

        processed_dates: list[datetime] = []

        async def mock_import_date(client, target_date):
            processed_dates.append(target_date)
            return 0

        with patch.object(service, "_import_date", mock_import_date):
            await service.run(None, from_date, to_date)

        assert len(processed_dates) == 2
        assert processed_dates[0] == datetime(2024, 6, 15)
        assert processed_dates[1] == datetime(2024, 6, 16)

    @pytest.mark.asyncio
    async def test_accumulates_total_vacancies(
        self,
        service: PracaByVacancyService,
        sample_vacancy: ParserVacancyResult,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 17)

        call_count = 0

        async def mock_stream(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                yield [sample_vacancy, sample_vacancy]
            else:
                yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch"),
        ):
            await service.run(None, from_date, to_date)

    @pytest.mark.asyncio
    async def test_ignores_query_parameter(
        self,
        service: PracaByVacancyService,
    ) -> None:
        from_date = datetime(2024, 6, 15)
        to_date = datetime(2024, 6, 16)

        async def mock_stream(client, target_date):
            return
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.praca_by.praca_service.import_vacancies_batch"),
        ):
            await service.run("Python developer", from_date, to_date)


class TestServiceInitialization:
    def test_creates_parser(self, mock_import_service: MagicMock) -> None:
        service = PracaByVacancyService(mock_import_service)

        assert service.parser is not None
        assert isinstance(service.parser, service.parser.__class__)

    def test_stores_import_service(self, mock_import_service: MagicMock) -> None:
        service = PracaByVacancyService(mock_import_service)

        assert service.import_service is mock_import_service
