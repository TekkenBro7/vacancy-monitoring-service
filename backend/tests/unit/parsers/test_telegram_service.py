from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.telegram.telegram_service import TelegramVacancyService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock(spec=ParserImportService)


@pytest.fixture
def service(mock_import_service: MagicMock) -> TelegramVacancyService:
    return TelegramVacancyService(mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="tg_12345",
        title="Python Developer",
        company_name="Tech Startup",
        company_external_id=None,
        salary_from=3000,
        salary_to=5000,
        currency="USD",
        city="Remote",
        address=None,
        experience="2+ years",
        education=None,
        employment="Full-time",
        schedule="Remote",
        is_remote=True,
        internship=False,
        vacancy_url="https://t.me/channel/12345",
    )


@pytest.fixture
def mock_import_batch() -> Any:
    with patch(
        "src.parsers.telegram.telegram_service._import_vacancies_batch",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


class TestImportVacancies:
    @pytest.mark.asyncio
    async def test_imports_single_batch(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_vacancies(from_date, to_date)

        assert result == 1
        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_imports_multiple_batches(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_vacancies(from_date, to_date)

        assert result == 3
        assert mock_import_batch.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_vacancies(
        self,
        service: TelegramVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_vacancies(from_date, to_date)

        assert result == 0
        mock_import_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_empty_batches(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield []
            yield [sample_vacancy]
            yield []

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_vacancies(from_date, to_date)

        assert result == 1
        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_sends_correct_payload(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service._import_vacancies(from_date, to_date)

        call_args = mock_import_batch.call_args
        payload = call_args[0][0]
        source_name = call_args[0][1]

        assert len(payload) == 1
        assert payload[0]["external_id"] == "tg_12345"
        assert payload[0]["title"] == "Python Developer"
        assert source_name is not None

    @pytest.mark.asyncio
    async def test_passes_correct_parameters_to_parser(
        self,
        service: TelegramVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        captured_args: dict[str, Any] = {}

        async def mock_stream(
            channel: str, from_date: datetime, to_date: datetime
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            captured_args["channel"] = channel
            captured_args["from_date"] = from_date
            captured_args["to_date"] = to_date
            return
            yield  # type: ignore[misc]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service._import_vacancies(from_date, to_date)

        assert captured_args["channel"] == service.channel
        assert captured_args["from_date"] == from_date
        assert captured_args["to_date"] == to_date


class TestRun:
    @pytest.mark.asyncio
    async def test_raises_error_when_from_date_is_none(
        self,
        service: TelegramVacancyService,
    ) -> None:
        with pytest.raises(ValueError, match="from_date and to_date are required"):
            await service.run(query=None, from_date=None, to_date=datetime(2024, 6, 2))

    @pytest.mark.asyncio
    async def test_raises_error_when_to_date_is_none(
        self,
        service: TelegramVacancyService,
    ) -> None:
        with pytest.raises(ValueError, match="from_date and to_date are required"):
            await service.run(query=None, from_date=datetime(2024, 6, 1), to_date=None)

    @pytest.mark.asyncio
    async def test_raises_error_when_both_dates_are_none(
        self,
        service: TelegramVacancyService,
    ) -> None:
        with pytest.raises(ValueError, match="from_date and to_date are required"):
            await service.run(query=None, from_date=None, to_date=None)

    @pytest.mark.asyncio
    async def test_runs_successfully_with_valid_dates(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service.run(query=None, from_date=from_date, to_date=to_date)

        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignores_query_parameter(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service.run(query="Python developer", from_date=from_date, to_date=to_date)

        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_parser_context_manager(
        self,
        service: TelegramVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        with patch.object(service, "parser") as mock_parser:
            mock_parser.stream_vacancies = mock_stream
            mock_parser.__aenter__ = AsyncMock(return_value=mock_parser)
            mock_parser.__aexit__ = AsyncMock(return_value=None)

            await service.run(query=None, from_date=from_date, to_date=to_date)

            mock_parser.__aenter__.assert_called_once()
            mock_parser.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_accumulates_total_vacancies(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]
            yield [sample_vacancy, sample_vacancy, sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service.run(query=None, from_date=from_date, to_date=to_date)

        assert mock_import_batch.call_count == 3


class TestServiceInitialization:
    def test_creates_parser(self, mock_import_service: MagicMock) -> None:
        service = TelegramVacancyService(mock_import_service)

        assert service.parser is not None

    def test_stores_import_service(self, mock_import_service: MagicMock) -> None:
        service = TelegramVacancyService(mock_import_service)

        assert service.import_service is mock_import_service

    def test_has_channel_configured(self, mock_import_service: MagicMock) -> None:
        service = TelegramVacancyService(mock_import_service)

        assert service.channel is not None
        assert isinstance(service.channel, str)


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_handles_large_batch(
        self,
        service: TelegramVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        from_date = datetime(2024, 6, 1)
        to_date = datetime(2024, 6, 2)

        large_batch = [
            ParserVacancyResult(external_id=f"tg_{i}", title=f"Developer {i}") for i in range(100)
        ]

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield large_batch

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_vacancies(from_date, to_date)

        assert result == 100
        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_same_from_and_to_date(
        self,
        service: TelegramVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        same_date = datetime(2024, 6, 1)

        async def mock_stream(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service.run(query=None, from_date=same_date, to_date=same_date)

        mock_import_batch.assert_called_once()
