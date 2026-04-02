from collections.abc import AsyncGenerator
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.epam.epam_service import EpamVacancyService
from src.parsers.services.parser_import_service import ParserImportService


@pytest.fixture
def mock_import_service() -> MagicMock:
    return MagicMock(spec=ParserImportService)


@pytest.fixture
def service(mock_import_service: MagicMock) -> EpamVacancyService:
    return EpamVacancyService(import_service=mock_import_service)


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="blt123",
        title="Python Developer",
        description="Description",
        company_name="EPAM Systems",
        company_external_id="epam",
        salary_from=None,
        salary_to=None,
        currency=None,
        city=None,
        address="Poland, Germany",
        experience="5+ years",
        education=None,
        employment=None,
        schedule=None,
        is_remote=True,
        published_at=None,
        internship=False,
        created_at=None,
        vacancy_url="https://careers.epam.com/vacancy/test",
        skills=["Python", "Django"],
    )


class TestEpamVacancyServiceInit:
    def test_initializes_with_import_service(self, mock_import_service: MagicMock) -> None:
        service = EpamVacancyService(import_service=mock_import_service)
        assert service.import_service == mock_import_service
        assert service.parser is not None

    def test_creates_epam_parser(self, mock_import_service: MagicMock) -> None:
        service = EpamVacancyService(import_service=mock_import_service)
        from src.parsers.epam.epam_parser import EpamParser

        assert isinstance(service.parser, EpamParser)


class TestRun:
    @pytest.mark.asyncio
    async def test_processes_vacancies_from_parser(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]
            yield [sample_vacancy, sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        assert mock_import_task.delay.call_count == 2

    @pytest.mark.asyncio
    async def test_sends_correct_payload_to_celery(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.core.config.epam_config.EPAM_SOURCE_NAME", "EPAM"),
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        mock_import_task.delay.assert_called_once()
        call_args = mock_import_task.delay.call_args
        payload = call_args[0][0]
        source_name = call_args[0][1]

        assert isinstance(payload, list)
        assert len(payload) == 1
        assert payload[0]["external_id"] == "blt123"
        assert payload[0]["title"] == "Python Developer"
        assert source_name == "EPAM"

    @pytest.mark.asyncio
    async def test_handles_empty_stream(self, service: EpamVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        mock_import_task.delay.assert_not_called()

    @pytest.mark.asyncio
    async def test_ignores_date_parameters(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run(
                query="Python",
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 12, 31),
            )

        assert mock_import_task.delay.call_count == 1

    @pytest.mark.asyncio
    async def test_logs_warning_for_date_filtering(self, service: EpamVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.parsers.epam.epam_service.logger") as mock_logger,
        ):
            mock_import_task.delay = MagicMock()
            await service.run(
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 12, 31),
            )

        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args
        assert "date filtering is not supported" in warning_call[0][0]

    @pytest.mark.asyncio
    async def test_does_not_log_warning_without_dates(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.parsers.epam.epam_service.logger") as mock_logger,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        warning_calls = [
            call for call in mock_logger.warning.call_args_list if "date filtering" in str(call)
        ]
        assert len(warning_calls) == 0

    @pytest.mark.asyncio
    async def test_counts_total_vacancies_correctly(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy, sample_vacancy]
            yield [sample_vacancy]
            yield [sample_vacancy, sample_vacancy, sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.parsers.epam.epam_service.logger") as mock_logger,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        info_calls = mock_logger.info.call_args_list
        final_log = info_calls[-1]
        assert "total 6 vacancies" in final_log[0][0] % final_log[0][1:]

    @pytest.mark.asyncio
    async def test_converts_vacancies_to_dict(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        call_args = mock_import_task.delay.call_args
        payload = call_args[0][0]

        assert isinstance(payload[0], dict)
        assert "external_id" in payload[0]
        assert "title" in payload[0]
        assert "skills" in payload[0]
        assert payload[0]["skills"] == ["Python", "Django"]

    @pytest.mark.asyncio
    async def test_calls_delay_for_each_batch(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]
            yield [sample_vacancy]
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        assert mock_import_task.delay.call_count == 3

    @pytest.mark.asyncio
    async def test_logs_info_at_start_and_end(self, service: EpamVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            return
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.parsers.epam.epam_service.logger") as mock_logger,
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        assert "starting" in info_calls[0][0][0]
        assert "finished" in info_calls[-1][0][0]

    @pytest.mark.asyncio
    async def test_uses_epam_source_name_from_config(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
            patch("src.core.config.epam_config.EPAM_SOURCE_NAME", "CustomEPAM"),
        ):
            mock_import_task.delay = MagicMock()
            await service.run()

        call_args = mock_import_task.delay.call_args
        source_name = call_args[0][1]
        assert source_name == "CustomEPAM"


class TestRunWithQuery:
    @pytest.mark.asyncio
    async def test_query_parameter_is_accepted(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            await service.run(query="Python Developer")

        assert mock_import_task.delay.call_count == 1


class TestRunErrorHandling:
    @pytest.mark.asyncio
    async def test_propagates_parser_exception(self, service: EpamVacancyService) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            raise RuntimeError("Parser failed")
            yield  # type: ignore[misc]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock()
            with pytest.raises(RuntimeError, match="Parser failed"):
                await service.run()

    @pytest.mark.asyncio
    async def test_propagates_celery_exception(
        self, service: EpamVacancyService, sample_vacancy: ParserVacancyResult
    ) -> None:
        async def mock_stream() -> AsyncGenerator[list[ParserVacancyResult], None]:
            yield [sample_vacancy]

        with (
            patch.object(service.parser, "stream_vacancies", mock_stream),
            patch("src.parsers.epam.epam_service.import_vacancies_batch") as mock_import_task,
        ):
            mock_import_task.delay = MagicMock(side_effect=Exception("Celery error"))
            with pytest.raises(Exception, match="Celery error"):
                await service.run()
