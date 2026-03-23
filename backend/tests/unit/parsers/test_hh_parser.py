from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from fastapi import status

from src.core.enums import HHWorkFormat
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.hh_ru.hh_parser import HHParser


@pytest.fixture
def parser() -> HHParser:
    return HHParser()


@pytest.fixture
def sample_vacancy_response() -> dict[str, Any]:
    return {
        "id": "12345",
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/12345",
        "area": {"id": "1", "name": "Москва"},
        "experience": {"id": "between1And3", "name": "1-3 года"},
        "employment": {"id": "full", "name": "Полная занятость"},
        "schedule": {"id": "remote", "name": "Удалённая работа"},
        "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
        "employer": {"id": "emp_123", "name": "Tech Company"},
        "snippet": {"responsibility": "Разработка на Python"},
        "work_format": [{"id": HHWorkFormat.REMOTE}],
        "published_at": "2024-06-15T10:30:00+0300",
        "created_at": "2024-06-14T08:00:00+0300",
        "internship": False,
    }


@pytest.fixture
def sample_api_response(sample_vacancy_response: dict[str, Any]) -> dict[str, Any]:
    return {
        "items": [sample_vacancy_response],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 100,
    }


class TestBuildParams:
    def test_builds_params_without_query(self, parser: HHParser) -> None:
        date_from = datetime(2024, 6, 1, 0, 0, 0)
        date_to = datetime(2024, 6, 2, 0, 0, 0)

        params = parser._build_params(0, None, date_from, date_to)

        assert params["page"] == 0
        assert params["per_page"] == 100
        assert params["date_from"] == "2024-06-01T00:00:00"
        assert params["date_to"] == "2024-06-02T00:00:00"
        assert "text" not in params

    def test_builds_params_with_query(self, parser: HHParser) -> None:
        params = parser._build_params(
            page=2,
            query="Python developer",
            date_from=datetime(2024, 6, 1),
            date_to=datetime(2024, 6, 2),
            per_page=50,
        )

        assert params["text"] == "Python developer"
        assert params["page"] == 2
        assert params["per_page"] == 50


class TestParseVacancy:
    def test_parses_full_vacancy(
        self, parser: HHParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        result = parser._parse_vacancy(sample_vacancy_response)

        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "12345"
        assert result.title == "Python Developer"
        assert result.company_name == "Tech Company"
        assert result.salary_from == 150000
        assert result.salary_to == 250000
        assert result.city == "Москва"
        assert result.is_remote is True

    def test_parses_minimal_vacancy(self, parser: HHParser) -> None:
        minimal = {"id": "99999", "name": "Junior Developer"}

        result = parser._parse_vacancy(minimal)

        assert result.external_id == "99999"
        assert result.title == "Junior Developer"
        assert result.salary_from is None
        assert result.company_name == "Unknown"
        assert result.is_remote is False

    def test_parses_vacancy_non_remote(self, parser: HHParser) -> None:
        vacancy = {
            "id": "123",
            "name": "Developer",
            "work_format": [{"id": "office"}],
        }

        result = parser._parse_vacancy(vacancy)

        assert result.is_remote is False


class TestRequest:
    @pytest.mark.asyncio
    async def test_successful_request(
        self, parser: HHParser, sample_api_response: dict[str, Any]
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
            result = await parser._request(mock_session, "https://api.hh.ru/vacancies", {})

        assert result == sample_api_response

    @pytest.mark.asyncio
    async def test_retries_on_403_then_succeeds(self, parser: HHParser) -> None:
        responses = [
            AsyncMock(status=status.HTTP_403_FORBIDDEN),
            AsyncMock(status=status.HTTP_200_OK, json=AsyncMock(return_value={"items": []})),
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
            result = await parser._request(mock_session, "https://api.hh.ru/vacancies", {})

        assert result == {"items": []}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self, parser: HHParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_response.text = AsyncMock(return_value="Error")

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="HH API request failed after retries"):
                await parser._request(mock_session, "https://api.hh.ru/vacancies", {})

    @pytest.mark.asyncio
    async def test_handles_timeout_error(self, parser: HHParser) -> None:
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(side_effect=TimeoutError())
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="HH API request failed after retries"):
                await parser._request(mock_session, "https://api.hh.ru/vacancies", {})

    @pytest.mark.asyncio
    async def test_handles_client_error(self, parser: HHParser) -> None:
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError())
        mock_cm.__aexit__ = AsyncMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="HH API request failed after retries"):
                await parser._request(mock_session, "https://api.hh.ru/vacancies", {})


class TestStreamVacancies:
    @pytest.mark.asyncio
    async def test_streams_single_page(
        self, parser: HHParser, sample_api_response: dict[str, Any]
    ) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_api_response

            results = []
            async for batch in parser.stream_vacancies(
                None, datetime(2024, 6, 1), datetime(2024, 6, 2)
            ):
                results.extend(batch)

            assert len(results) == 1
            assert isinstance(results[0], ParserVacancyResult)
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_streams_multiple_pages(
        self, parser: HHParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        responses = [
            {"items": [sample_vacancy_response], "found": 150, "pages": 2, "page": 0},
            {"items": [sample_vacancy_response], "found": 150, "pages": 2, "page": 1},
        ]

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = responses

            results = []
            async for batch in parser.stream_vacancies(
                None, datetime(2024, 6, 1), datetime(2024, 6, 2)
            ):
                results.extend(batch)

            assert len(results) == 2
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_streams_empty_results(self, parser: HHParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": [], "found": 0, "pages": 0}

            results = []
            async for batch in parser.stream_vacancies(
                "nonexistent", datetime(2024, 6, 1), datetime(2024, 6, 2)
            ):
                results.extend(batch)

            assert len(results) == 0


class TestSearchVacancies:
    @pytest.mark.asyncio
    async def test_returns_total_found(self, parser: HHParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": [], "found": 1500, "pages": 15}

            result = await parser.search_vacancies(
                "Python", datetime(2024, 6, 1), datetime(2024, 6, 2)
            )

            assert result == 1500

    @pytest.mark.asyncio
    async def test_returns_zero_when_found_missing(self, parser: HHParser) -> None:
        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": [], "pages": 0}

            result = await parser.search_vacancies(None, datetime(2024, 6, 1), datetime(2024, 6, 2))

            assert result == 0


class TestGetVacancy:
    @pytest.mark.asyncio
    async def test_returns_vacancy_data_on_success(
        self, parser: HHParser, sample_vacancy_response: dict[str, Any]
    ) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_200_OK
        mock_response.text = AsyncMock(return_value="{}")
        mock_response.json = AsyncMock(return_value=sample_vacancy_response)

        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response_cm.__aexit__ = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response_cm)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result == sample_vacancy_response

    @pytest.mark.asyncio
    async def test_returns_none_on_404(self, parser: HHParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_404_NOT_FOUND
        mock_response.text = AsyncMock(return_value="Not found")

        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response_cm.__aexit__ = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response_cm)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("99999")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_429_rate_limit(self, parser: HHParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_429_TOO_MANY_REQUESTS
        mock_response.text = AsyncMock(return_value="Rate limit exceeded")

        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response_cm.__aexit__ = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response_cm)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_other_error_status(self, parser: HHParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_response.text = AsyncMock(return_value="Internal server error")

        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response_cm.__aexit__ = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response_cm)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_timeout(self, parser: HHParser) -> None:
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(side_effect=TimeoutError())
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_client_error(self, parser: HHParser) -> None:
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError())
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_unexpected_exception(self, parser: HHParser) -> None:
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(side_effect=Exception("Unexpected error"))
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await parser.get_vacancy("12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_builds_correct_url(self, parser: HHParser) -> None:
        mock_response = AsyncMock()
        mock_response.status = status.HTTP_200_OK
        mock_response.text = AsyncMock(return_value="{}")
        mock_response.json = AsyncMock(return_value={"id": "12345"})

        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response_cm.__aexit__ = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response_cm)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            with patch("src.core.config.hh_config.HH_BASE_URL", "https://api.hh.ru/vacancies"):
                await parser.get_vacancy("12345")

        mock_session.get.assert_called_once_with("https://api.hh.ru/vacancies/12345")
