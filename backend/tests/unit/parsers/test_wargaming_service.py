from collections.abc import AsyncGenerator
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.wargaming.wargaming_service import WargamingVacancyService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock(spec=ParserImportService)


@pytest.fixture
def service(mock_import_service: MagicMock) -> WargamingVacancyService:
    return WargamingVacancyService(import_service=mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="vacancy_12345_berlin",
        title="Python Developer",
        description="<p>Job description</p>",
        company_name="Wargaming",
        company_external_id="wargaming",
        salary_from=None,
        salary_to=None,
        currency=None,
        city="Berlin",
        address="Berlin, Germany",
        experience="5+ years",
        education=None,
        employment="Engineering",
        schedule=None,
        is_remote=True,
        published_at=None,
        internship=False,
        created_at=None,
        vacancy_url="https://wargaming.com/en/careers/vacancy_12345_berlin/",
        skills=[],
    )


class TestWargamingVacancyServiceInit:
    def test_initializes_with_import_service(self, mock_import_service: MagicMock) -> None:
        service = WargamingVacancyService(import_service=mock_import_service)
        assert service.import_service == mock_import_service
        assert service.parser is not None

    def test_creates_wargaming_parser(self, mock_import_service: MagicMock) -> None:
        service = WargamingVacancyService(import_service=mock_import_service)
        from src.parsers.wargaming.wargaming_parser import WargamingParser

        assert isinstance(service.parser, WargamingParser)


class TestRun:
    @pytest.mark.asyncio
    async def test_processes_vacancies_from_parser(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]
            yield [sample_vacancy, sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        assert mock_import.call_count == 2

    @pytest.mark.asyncio
    async def test_sends_correct_payload(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch(
                "src.parsers.wargaming.wargaming_service.wargaming_config.WARGAMING_SOURCE_NAME",
                "Wargaming",
            ),
        ):
            await service.run()

        mock_import.assert_called_once()
        call_args = mock_import.call_args
        payload = call_args[0][0]
        source_name = call_args[0][1]

        assert isinstance(payload, list)
        assert len(payload) == 1
        assert payload[0]["external_id"] == "vacancy_12345_berlin"
        assert payload[0]["title"] == "Python Developer"
        assert payload[0]["company_name"] == "Wargaming"
        assert source_name == "Wargaming"

    @pytest.mark.asyncio
    async def test_handles_empty_stream(self, service: WargamingVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        mock_import.assert_not_called()

    @pytest.mark.asyncio
    async def test_logs_warning_for_date_filtering(self, service: WargamingVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch("src.parsers.wargaming.wargaming_service.logger") as mock_logger,
        ):
            await service.run(
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 12, 31),
            )

        mock_logger.warning.assert_called()
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any("date filtering not supported" in call for call in warning_calls)

    @pytest.mark.asyncio
    async def test_logs_warning_for_query_filtering(self, service: WargamingVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch("src.parsers.wargaming.wargaming_service.logger") as mock_logger,
        ):
            await service.run(query="Python Developer")

        mock_logger.warning.assert_called()
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any("query filtering not supported" in call for call in warning_calls)

    @pytest.mark.asyncio
    async def test_does_not_log_warning_without_filters(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch("src.parsers.wargaming.wargaming_service.logger") as mock_logger,
        ):
            await service.run()

        warning_calls = [
            call for call in mock_logger.warning.call_args_list if "not supported" in str(call)
        ]
        assert len(warning_calls) == 0

    @pytest.mark.asyncio
    async def test_counts_total_vacancies_correctly(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]
            yield [sample_vacancy, sample_vacancy, sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch("src.parsers.wargaming.wargaming_service.logger") as mock_logger,
        ):
            await service.run()

        info_calls = mock_logger.info.call_args_list
        final_log = info_calls[-1]

        log_message = (
            final_log[0][0] % final_log[0][1:] if len(final_log[0]) > 1 else final_log[0][0]
        )
        assert "6" in log_message or "total 6" in str(final_log)

    @pytest.mark.asyncio
    async def test_converts_vacancies_to_dict(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        call_args = mock_import.call_args
        payload = call_args[0][0]

        assert isinstance(payload[0], dict)
        assert "external_id" in payload[0]
        assert "title" in payload[0]
        assert "company_name" in payload[0]
        assert "is_remote" in payload[0]
        assert payload[0]["is_remote"] is True

    @pytest.mark.asyncio
    async def test_calls_import_for_each_batch(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]
            yield [sample_vacancy]
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        assert mock_import.call_count == 3


class TestRunWithParameters:
    @pytest.mark.asyncio
    async def test_query_parameter_is_ignored(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run(query="Python Developer")

        assert mock_import.call_count == 1

    @pytest.mark.asyncio
    async def test_date_parameters_are_ignored(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run(
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 12, 31),
            )

        assert mock_import.call_count == 1

    @pytest.mark.asyncio
    async def test_all_parameters_together(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
            patch("src.parsers.wargaming.wargaming_service.logger") as mock_logger,
        ):
            await service.run(
                query="Python",
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 12, 31),
            )

        warning_calls = mock_logger.warning.call_args_list
        assert len(warning_calls) == 2


class TestRunErrorHandling:
    @pytest.mark.asyncio
    async def test_propagates_parser_exception(self, service: WargamingVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            raise RuntimeError("Parser failed")
            yield  # type: ignore[misc]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            with pytest.raises(RuntimeError, match="Parser failed"):
                await service.run()

    @pytest.mark.asyncio
    async def test_propagates_import_exception(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock(side_effect=Exception("Import error"))

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            with pytest.raises(Exception, match="Import error"):
                await service.run()


class TestVacancyPayload:
    @pytest.mark.asyncio
    async def test_payload_contains_all_fields(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        call_args = mock_import.call_args
        payload = call_args[0][0][0]

        expected_fields = [
            "external_id",
            "title",
            "description",
            "company_name",
            "company_external_id",
            "salary_from",
            "salary_to",
            "currency",
            "city",
            "address",
            "experience",
            "education",
            "employment",
            "schedule",
            "is_remote",
            "published_at",
            "internship",
            "created_at",
            "vacancy_url",
            "skills",
        ]

        for field in expected_fields:
            assert field in payload, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_payload_values_match_vacancy(
        self, service: WargamingVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        mock_import = AsyncMock()

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch(
                "src.parsers.wargaming.wargaming_service._import_vacancies_batch",
                mock_import,
            ),
        ):
            await service.run()

        call_args = mock_import.call_args
        payload = call_args[0][0][0]

        assert payload["external_id"] == "vacancy_12345_berlin"
        assert payload["title"] == "Python Developer"
        assert payload["company_name"] == "Wargaming"
        assert payload["city"] == "Berlin"
        assert payload["address"] == "Berlin, Germany"
        assert payload["experience"] == "5+ years"
        assert payload["is_remote"] is True
        assert payload["internship"] is False
        assert payload["vacancy_url"] == "https://wargaming.com/en/careers/vacancy_12345_berlin/"
