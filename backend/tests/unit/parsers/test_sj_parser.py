from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from fastapi import status

from src.core.enums import SJPlaceOfWork
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.superjob.sj_parser import SJParser


@pytest.fixture
def parser() -> SJParser:
    return SJParser()


@pytest.fixture
def sample_vacancy_response() -> dict[str, Any]:
    return {
        "id": 12345,
        "profession": "Python Developer",
        "link": "https://superjob.ru/vacancy/12345",
        "town": {"id": 4, "title": "Москва"},
        "experience": {"id": 2, "title": "от 1 года"},
        "type_of_work": {"id": 6, "title": "Полный рабочий день"},
        "place_of_work": {"id": SJPlaceOfWork.REMOTE, "title": "Удалённая работа"},
        "payment_from": 150000,
        "payment_to": 250000,
        "currency": "rub",
        "firm_name": "Tech Company",
        "client": {"id": 789, "title": "Tech Company Inc"},
        "work": "Разработка на Python",
        "candidat": "Опыт от 1 года",
        "compensation": "ДМС, обеды",
        "date_published": 1718444400,  # 2024-06-15T10:00:00 UTC
    }


@pytest.fixture
def sample_api_response(sample_vacancy_response: dict[str, Any]) -> dict[str, Any]:
    return {
        "objects": [sample_vacancy_response],
        "total": 1,
        "more": False,
    }


class TestBuildParams:
    def test_builds_params_without_query(self, parser: SJParser) -> None:
        date_from = datetime(2024, 6, 1, 0, 0, 0, tzinfo=UTC)
        date_to = datetime(2024, 6, 2, 0, 0, 0, tzinfo=UTC)

        params = parser._build_params(0, None, date_from, date_to)

        assert params["page"] == 0
        assert params["count"] == 40
        assert params["date_published_from"] == int(date_from.timestamp())
        assert params["date_published_to"] == int(date_to.timestamp())
        assert params["order_field"] == "date"
        assert params["order_direction"] == "desc"
        assert "keyword" not in params

    def test_builds_params_with_query(self, parser: SJParser) -> None:
        date_from = datetime(2024, 6, 1, tzinfo=UTC)
        date_to = datetime(2024, 6, 2, tzinfo=UTC)

        params = parser._build_params(
            page=2,
            query="Python developer",
            date_from=date_from,
            date_to=date_to,
        )

        assert params["keyword"] == "Python developer"
        assert params["page"] == 2


class TestParseVacancy:
    def test_parses_full_vacancy(
        self, parser: SJParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        result = parser._parse_vacancy(sample_vacancy_response)

        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "12345"
        assert result.title == "Python Developer"
        assert result.company_name == "Tech Company"
        assert result.company_external_id == "789"
        assert result.salary_from == 150000
        assert result.salary_to == 250000
        assert result.currency == "rub"
        assert result.city == "Москва"
        assert result.experience == "от 1 года"
        assert result.employment == "Полный рабочий день"
        assert result.is_remote is True
        assert result.vacancy_url == "https://superjob.ru/vacancy/12345"
        assert result.published_at is not None

    def test_parses_minimal_vacancy(self, parser: SJParser) -> None:
        minimal = {"id": 99999, "profession": "Junior Developer"}

        result = parser._parse_vacancy(minimal)

        assert result.external_id == "99999"
        assert result.title == "Junior Developer"
        assert result.salary_from is None
        assert result.salary_to is None
        assert result.company_name is None
        assert result.is_remote is False

    def test_parses_vacancy_non_remote(self, parser: SJParser) -> None:
        vacancy = {
            "id": 123,
            "profession": "Developer",
            "place_of_work": {"id": SJPlaceOfWork.ON_SITE, "title": "На территории работодателя"},
        }

        result = parser._parse_vacancy(vacancy)

        assert result.is_remote is False

    def test_parses_description_parts(self, parser: SJParser) -> None:
        vacancy = {
            "id": 123,
            "profession": "Developer",
            "work": "Писать код",
            "candidat": "Знать Python",
            "compensation": "Печеньки",
        }

        result = parser._parse_vacancy(vacancy)

        assert result.description is not None
        assert "Обязанности: Писать код" in result.description
        assert "Требования: Знать Python" in result.description
        assert "Условия: Печеньки" in result.description

    def test_handles_zero_salary_as_none(self, parser: SJParser) -> None:
        vacancy = {
            "id": 123,
            "profession": "Developer",
            "payment_from": 0,
            "payment_to": 0,
        }

        result = parser._parse_vacancy(vacancy)

        assert result.salary_from is None
        assert result.salary_to is None

    def test_uses_client_title_when_firm_name_missing(self, parser: SJParser) -> None:
        vacancy = {
            "id": 123,
            "profession": "Developer",
            "client": {"id": 456, "title": "Company from Client"},
        }

        result = parser._parse_vacancy(vacancy)

        assert result.company_name == "Company from Client"
        assert result.company_external_id == "456"

    def test_parses_published_at_timestamp(self, parser: SJParser) -> None:
        timestamp = 1718444400  # 2024-06-15T10:00:00 UTC
        vacancy = {
            "id": 123,
            "profession": "Developer",
            "date_published": timestamp,
        }

        result = parser._parse_vacancy(vacancy)

        assert result.published_at == datetime.fromtimestamp(timestamp, tz=UTC)


class TestRequest:
    @pytest.mark.asyncio
    async def test_successful_request(
        self, parser: SJParser, sample_api_response: dict[str, Any]
    ) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_200_OK
        mock_response.json = AsyncMock(return_value=sample_api_response)

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(
                mock_session, "https://api.superjob.ru/2.0/vacancies", {}
            )

        assert result == sample_api_response

    @pytest.mark.asyncio
    async def test_retries_on_503_then_succeeds(self, parser: SJParser) -> None:
        responses = [
            AsyncMock(status=status.HTTP_503_SERVICE_UNAVAILABLE),
            AsyncMock(status=status.HTTP_200_OK, json=AsyncMock(return_value={"objects": []})),
        ]
        call_count = 0

        async def mock_aenter(self: Any) -> AsyncMock:
            nonlocal call_count
            result = responses[call_count]
            call_count += 1
            return result

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = mock_aenter
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(
                mock_session, "https://api.superjob.ru/2.0/vacancies", {}
            )

        assert result == {"objects": []}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_429_then_succeeds(self, parser: SJParser) -> None:
        responses = [
            AsyncMock(status=status.HTTP_429_TOO_MANY_REQUESTS),
            AsyncMock(status=status.HTTP_200_OK, json=AsyncMock(return_value={"objects": []})),
        ]
        call_count = 0

        async def mock_aenter(self: Any) -> AsyncMock:
            nonlocal call_count
            result = responses[call_count]
            call_count += 1
            return result

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = mock_aenter
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(
                mock_session, "https://api.superjob.ru/2.0/vacancies", {}
            )

        assert result == {"objects": []}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self, parser: SJParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_response.text = AsyncMock(return_value="Error")

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="SJ API request failed after retries"):
                await parser._request(mock_session, "https://api.superjob.ru/2.0/vacancies", {})

    @pytest.mark.asyncio
    async def test_handles_timeout_error(self, parser: SJParser) -> None:
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(side_effect=TimeoutError())
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="SJ API request failed after retries"):
                await parser._request(mock_session, "https://api.superjob.ru/2.0/vacancies", {})

    @pytest.mark.asyncio
    async def test_handles_client_error(self, parser: SJParser) -> None:
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError())
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="SJ API request failed after retries"):
                await parser._request(mock_session, "https://api.superjob.ru/2.0/vacancies", {})


class TestFetchAllVacancies:
    @pytest.mark.asyncio
    async def test_fetches_single_page(
        self, parser: SJParser, sample_api_response: dict[str, Any]
    ) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_api_response

            results = await parser.fetch_all_vacancies(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert len(results) == 1
            assert isinstance(results[0], ParserVacancyResult)
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetches_multiple_pages(
        self, parser: SJParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        responses = [
            {"objects": [sample_vacancy_response], "total": 30, "more": True},
            {"objects": [sample_vacancy_response], "total": 30, "more": False},
        ]

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = responses

            results = await parser.fetch_all_vacancies(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert len(results) == 2
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_fetches_empty_results(self, parser: SJParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"objects": [], "total": 0, "more": False}

            results = await parser.fetch_all_vacancies(
                "nonexistent", datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_stops_when_no_more_pages(
        self, parser: SJParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "objects": [sample_vacancy_response],
                "total": 1,
                "more": False,
            }

            results = await parser.fetch_all_vacancies(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert len(results) == 1
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_stops_at_max_pages(
        self, parser: SJParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        with (
            patch.object(parser, "_request", new_callable=AsyncMock) as mock_request,
            patch("src.core.config.super_job_config.SJ_MAX_PAGES", 3),
        ):
            mock_request.return_value = {
                "objects": [sample_vacancy_response],
                "total": 1000,
                "more": True,
            }

            results = await parser.fetch_all_vacancies(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert mock_request.call_count == 3
            assert len(results) == 3


class TestSearchVacancies:
    @pytest.mark.asyncio
    async def test_returns_total_found(self, parser: SJParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"objects": [], "total": 1500, "more": True}

            result = await parser.search_vacancies(
                "Python", datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert result == 1500

    @pytest.mark.asyncio
    async def test_returns_zero_when_total_missing(self, parser: SJParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"objects": []}

            result = await parser.search_vacancies(
                None, datetime(2024, 6, 1, tzinfo=UTC), datetime(2024, 6, 2, tzinfo=UTC)
            )

            assert result == 0
