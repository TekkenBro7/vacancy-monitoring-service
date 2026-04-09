from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.superjob.sj_service import SJVacancyService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(mock_import_service: MagicMock) -> SJVacancyService:
    return SJVacancyService(mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="12345",
        title="Python Developer",
        company_name="Tech Company",
    )


@pytest.fixture
def mock_celery_task() -> Any:
    """Mock the async _import_vacancies_batch function."""
    with patch(
        "src.parsers.superjob.sj_service._import_vacancies_batch",
        new_callable=AsyncMock,
    ) as mock_task:
        yield mock_task


class TestImportRange:
    @pytest.mark.asyncio
    async def test_imports_single_batch(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "fetch_all_vacancies", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [sample_vacancy]

            result = await service._import_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 1
        mock_celery_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_imports_multiple_vacancies(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "fetch_all_vacancies", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [sample_vacancy, sample_vacancy, sample_vacancy]

            result = await service._import_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 3
        mock_celery_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_imports_empty_results(
        self,
        service: SJVacancyService,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "fetch_all_vacancies", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = []

            result = await service._import_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 0
        mock_celery_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_correct_payload(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "fetch_all_vacancies", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [sample_vacancy]

            await service._import_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        # Теперь проверяем call_args напрямую (не .delay.call_args)
        call_args = mock_celery_task.call_args
        payload = call_args[0][0]
        source_name = call_args[0][1]

        assert isinstance(payload, list)
        assert payload[0]["external_id"] == "12345"
        assert payload[0]["title"] == "Python Developer"
        assert source_name == "SuperJob"


class TestParseRange:
    @pytest.mark.asyncio
    async def test_imports_when_under_limit(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_search.return_value = 200
            mock_fetch.return_value = [sample_vacancy]

            result = await service._parse_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 1
        mock_search.assert_called_once()
        mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_vacancies(
        self,
        service: SJVacancyService,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "search_vacancies", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = 0

            result = await service._parse_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 0
        mock_celery_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_splits_when_over_limit(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        call_count = 0

        async def mock_search(*args: Any) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return 600
            return 200

        with (
            patch.object(service.parser, "search_vacancies", mock_search),
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_fetch.return_value = [sample_vacancy]

            result = await service._parse_range(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

        assert result == 2
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_imports_when_cannot_split_further(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        start = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
        end = datetime(2024, 6, 1, 12, 0, 30, tzinfo=UTC)

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_search.return_value = 600
            mock_fetch.return_value = [sample_vacancy]

            result = await service._parse_range(None, start, end)

        assert result == 1
        mock_fetch.assert_called_once()


class TestRun:
    @pytest.mark.asyncio
    async def test_processes_single_day(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_search.return_value = 100
            mock_fetch.return_value = [sample_vacancy]

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 2, tzinfo=UTC),
            )

        mock_celery_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_processes_multiple_days(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_search.return_value = 100
            mock_fetch.return_value = [sample_vacancy]

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 4, tzinfo=UTC),
            )

        assert mock_celery_task.call_count == 3

    @pytest.mark.asyncio
    async def test_processes_with_query(
        self,
        service: SJVacancyService,
        sample_vacancy: ParserVacancyResult,
        mock_celery_task: AsyncMock,
    ) -> None:
        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(
                service.parser, "fetch_all_vacancies", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_search.return_value = 100
            mock_fetch.return_value = [sample_vacancy]

            await service.run(
                query="Python",
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 2, tzinfo=UTC),
            )

        call_args = mock_search.call_args
        assert call_args[0][0] == "Python"

    @pytest.mark.asyncio
    async def test_handles_empty_date_range(
        self,
        service: SJVacancyService,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "search_vacancies", new_callable=AsyncMock
        ) as mock_search:
            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 1, tzinfo=UTC),
            )

        mock_search.assert_not_called()
        mock_celery_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_zero_vacancies_per_day(
        self,
        service: SJVacancyService,
        mock_celery_task: AsyncMock,
    ) -> None:
        with patch.object(
            service.parser, "search_vacancies", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = 0

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 3, tzinfo=UTC),
            )

        assert mock_search.call_count == 2
        mock_celery_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_accumulates_total_across_days(
        self,
        service: SJVacancyService,
        mock_celery_task: AsyncMock,
    ) -> None:
        vacancies_per_day = [
            [ParserVacancyResult(external_id="1", title="Dev1")],
            [
                ParserVacancyResult(external_id="2", title="Dev2"),
                ParserVacancyResult(external_id="3", title="Dev3"),
            ],
            [ParserVacancyResult(external_id="4", title="Dev4")],
        ]
        current_day = 0

        async def mock_fetch(*args: Any) -> list[ParserVacancyResult]:
            nonlocal current_day
            result = vacancies_per_day[current_day]
            current_day += 1
            return result

        with (
            patch.object(service.parser, "search_vacancies", new_callable=AsyncMock) as mock_search,
            patch.object(service.parser, "fetch_all_vacancies", mock_fetch),
        ):
            mock_search.return_value = 100

            await service.run(
                query=None,
                from_date=datetime(2024, 6, 1, tzinfo=UTC),
                to_date=datetime(2024, 6, 4, tzinfo=UTC),
            )

        assert mock_celery_task.call_count == 3
