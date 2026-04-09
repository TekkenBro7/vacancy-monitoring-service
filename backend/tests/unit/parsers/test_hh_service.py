from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.hh_ru.hh_service import HHVacancyService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(mock_import_service: MagicMock) -> HHVacancyService:
    return HHVacancyService(mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="12345",
        title="Python Developer",
        company_name="Tech Company",
    )


@pytest.fixture
def mock_import_batch() -> Any:
    with patch(
        "src.parsers.hh_ru.hh_service._import_vacancies_batch",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


class TestImportRange:
    @pytest.mark.asyncio
    async def test_imports_single_batch(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        assert result == 1
        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_imports_multiple_batches(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        assert result == 3
        assert mock_import_batch.call_count == 2

    @pytest.mark.asyncio
    async def test_imports_empty_results(
        self,
        service: HHVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            return
            yield

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            result = await service._import_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        assert result == 0
        mock_import_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_correct_payload(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with patch.object(service.parser, "stream_vacancies", mock_stream):
            await service._import_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        call_args = mock_import_batch.call_args
        payload = call_args[0][0]

        assert isinstance(payload, list)
        assert payload[0]["external_id"] == "12345"
        assert payload[0]["title"] == "Python Developer"


class TestParseRange:
    @pytest.mark.asyncio
    async def test_imports_when_under_limit(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            mock_search.return_value = 500

            result = await service._parse_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        assert result == 1
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_splits_when_over_limit(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        call_count = 0

        async def mock_search(*args: Any) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return 2500
            return 500

        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "search_vacancies", mock_search),
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            result = await service._parse_range(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

        assert result == 2
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_returns_zero_when_cannot_split(
        self,
        service: HHVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        start = datetime(2024, 6, 1, 12, 0, 0)
        end = start

        with patch.object(
            service.parser, "search_vacancies", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = 2500

            result = await service._parse_range(None, start, end)

        assert result == 0


class TestRun:
    @pytest.mark.asyncio
    async def test_processes_single_day(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            mock_search.return_value = 100

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1),
                to_date=datetime(2024, 6, 2),
            )

        mock_import_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_processes_multiple_days(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            mock_search.return_value = 100

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1),
                to_date=datetime(2024, 6, 4),
            )

        assert mock_import_batch.call_count == 3

    @pytest.mark.asyncio
    async def test_processes_with_query(
        self,
        service: HHVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_import_batch: AsyncMock,
    ) -> None:
        async def mock_stream(*args: Any) -> Any:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            mock_search.return_value = 100

            await service.run(
                query="Python",
                from_date=datetime(2024, 6, 1),
                to_date=datetime(2024, 6, 2),
            )

        call_args = mock_search.call_args
        assert call_args[0][0] == "Python"

    @pytest.mark.asyncio
    async def test_handles_empty_date_range(
        self,
        service: HHVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "search_vacancies", new_callable=AsyncMock
        ) as mock_search:
            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1),
                to_date=datetime(2024, 6, 1),
            )

        mock_search.assert_not_called()
        mock_import_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_accumulates_total_across_days(
        self,
        service: HHVacancyService,
        mock_import_batch: AsyncMock,
    ) -> None:
        day_counts = [3, 5, 2]
        current_day = 0

        async def mock_stream(*args: Any) -> Any:
            nonlocal current_day
            for _ in range(day_counts[current_day]):
                yield [ParserVacancyResult(external_id=f"id_{current_day}", title="Dev")]
            current_day += 1

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "stream_vacancies", mock_stream),
        ):
            mock_search.return_value = 100

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1),
                to_date=datetime(2024, 6, 4),
            )

        assert mock_import_batch.call_count == 10
