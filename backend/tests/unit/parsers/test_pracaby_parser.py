from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from freezegun import freeze_time

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.praca_by.praca_parser import PracaByParser


@pytest.fixture
def parser() -> PracaByParser:
    return PracaByParser()


@pytest.fixture
def sample_vacancy_html() -> str:
    return """
    <html>
    <body>
        <h1>Python Developer</h1>
        <div class="vacancy__org-name">
            <a href="/organization/12345/">Tech Company</a>
        </div>
        <div class="vacancy__city">Минск</div>
        <div class="job-address">Минск, ул. Тестовая, 123</div>
        <div class="vacancy__salary">2000 - 3500 руб.</div>
        <div class="vacancy__description">
            <div class="description"><p>Описание вакансии</p></div>
        </div>
        <p class="vacancy__experience">Опыт работы от 1 года</p>
        <p class="vacancy__education">Высшее образование</p>
        <div class="vacancy-required__first-block">
            <div class="vacancy__item">График работы: Полный день</div>
            <div class="vacancy__item">Занятость: Полная</div>
            <div class="vacancy__item">Характер работы: На территории работодателя</div>
        </div>
        <div class="vacancy__common-info">
            <time datetime="2024-06-15T10:00:00+03:00">15 июня</time>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_html_remote() -> str:
    return """
    <html>
    <body>
        <h1>Remote Developer</h1>
        <div class="vacancy__org-name">
            <a href="/organization/999/">Remote Corp</a>
        </div>
        <div class="vacancy__city">Минск</div>
        <div class="vacancy-required__first-block">
            <div class="vacancy__item">Характер работы: Удалённая работа</div>
            <div class="vacancy__item">Занятость: Полная, стажировка</div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_html_minimal() -> str:
    return """
    <html>
    <body>
        <h1>Junior Developer</h1>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_html() -> str:
    return """
    <html>
    <body>
        <article>
            <a class="vac-small__title-link" href="/vacancy/111/">Vacancy 1</a>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        <article>
            <a class="vac-small__title-link" href="/vacancy/222/">Vacancy 2</a>
            <div class="vac-small__upped-time">вчера</div>
        </article>
        <article>
            <a class="vac-small__title-link" href="/vacancy/333/">Vacancy 3</a>
            <div class="vac-small__upped-time">15 марта</div>
        </article>
    </body>
    </html>
    """


class TestParseRelativeDate:
    @freeze_time("2024-06-15")
    def test_parses_today(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("сегодня")
        assert result == date(2024, 6, 15)

    @freeze_time("2024-06-15")
    def test_parses_yesterday(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("вчера")
        assert result == date(2024, 6, 14)

    @freeze_time("2024-06-15")
    def test_parses_date_with_month(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("10 марта")
        assert result == date(2024, 3, 10)

    @freeze_time("2024-06-15")
    def test_parses_date_with_year(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("25 декабря 2023")
        assert result == date(2023, 12, 25)

    @freeze_time("2024-06-15")
    def test_parses_may_mya(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("5 мая")
        assert result == date(2024, 5, 5)

    @freeze_time("2024-06-15")
    def test_handles_invalid_date(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("invalid")
        assert result == date(2024, 6, 15)

    @freeze_time("2024-06-15")
    def test_handles_empty_string(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("")
        assert result == date(2024, 6, 15)

    @freeze_time("2024-06-15")
    def test_case_insensitive(self, parser: PracaByParser) -> None:
        result = parser._parse_relative_date("СЕГОДНЯ")
        assert result == date(2024, 6, 15)


class TestParseSalary:
    def test_parses_salary_range(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">2000 - 3500 руб.</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert salary_from == 2000
        assert salary_to == 3500
        assert currency == "BYN"

    def test_parses_salary_from_only(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">от 2000 руб.</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert salary_from == 2000
        assert salary_to is None

    def test_parses_salary_to_only(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">до 5000 руб.</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert salary_from is None
        assert salary_to == 5000

    def test_parses_usd_salary(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">1000 - 2000 $</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert currency == "USD"

    def test_parses_eur_salary(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">1000 - 2000 €</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert currency == "EUR"

    def test_returns_none_when_no_salary(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = "<div>No salary here</div>"
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert salary_from is None
        assert salary_to is None
        assert currency is None

    def test_parses_salary_with_spaces(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div class="vacancy__salary">2 000 - 3 500 руб.</div>'
        tree = HTMLParser(html)

        salary_from, salary_to, currency = parser._parse_salary(tree)

        assert salary_from == 2000
        assert salary_to == 3500


class TestParseVacancyPage:
    def test_parses_full_vacancy(self, parser: PracaByParser, sample_vacancy_html: str) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_html, "12345", "https://praca.by/vacancy/12345/"
        )

        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "12345"
        assert result.title == "Python Developer"
        assert result.company_name == "Tech Company"
        assert result.company_external_id == "12345"
        assert result.city == "Минск"
        assert result.address == "Минск, ул. Тестовая, 123"
        assert result.salary_from == 2000
        assert result.salary_to == 3500
        assert result.currency == "BYN"
        assert result.experience == "Опыт работы от 1 года"
        assert result.education == "Высшее образование"
        assert result.schedule == "Полный день"
        assert result.employment == "Полная"
        assert result.is_remote is False
        assert result.internship is False
        assert result.vacancy_url == "https://praca.by/vacancy/12345/"

    def test_parses_remote_vacancy(
        self, parser: PracaByParser, sample_vacancy_html_remote: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_html_remote, "999", "https://praca.by/vacancy/999/"
        )

        assert result.is_remote is True
        assert result.internship is True

    def test_parses_minimal_vacancy(
        self, parser: PracaByParser, sample_vacancy_html_minimal: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_html_minimal, "111", "https://praca.by/vacancy/111/"
        )

        assert result.title == "Junior Developer"
        assert result.company_name is None
        assert result.salary_from is None
        assert result.salary_to is None
        assert result.is_remote is False

    def test_parses_description_as_html(
        self, parser: PracaByParser, sample_vacancy_html: str
    ) -> None:
        result = parser._parse_vacancy_page(sample_vacancy_html, "123", "url")

        assert result.description is not None
        assert "<p>" in result.description


class TestScanPageDates:
    @freeze_time("2024-06-15")
    def test_scans_page_dates(self, parser: PracaByParser, sample_search_page_html: str) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_search_page_html)
        result = parser._scan_page_dates(tree)

        assert len(result) == 3
        assert result["111"] == date(2024, 6, 15)  # сегодня
        assert result["222"] == date(2024, 6, 14)  # вчера
        assert result["333"] == date(2024, 3, 15)  # 15 марта

    def test_handles_empty_page(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser("<html><body></body></html>")
        result = parser._scan_page_dates(tree)

        assert len(result) == 0

    def test_skips_articles_without_link(self, parser: PracaByParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <article>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        """
        tree = HTMLParser(html)
        result = parser._scan_page_dates(tree)

        assert len(result) == 0


class TestRequest:
    @pytest.mark.asyncio
    async def test_successful_request(self, parser: PracaByParser) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Success</html>"

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(mock_client, "https://praca.by/test/")

        assert result == "<html>Success</html>"

    @pytest.mark.asyncio
    async def test_returns_none_on_bad_status(self, parser: PracaByParser) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(mock_client, "https://praca.by/test/")

        assert result is None

    @pytest.mark.asyncio
    async def test_retries_on_429(self, parser: PracaByParser) -> None:
        responses = [
            MagicMock(status_code=429),
            MagicMock(status_code=200, text="<html>Success</html>"),
        ]

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=responses)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(mock_client, "https://praca.by/test/")

        assert result == "<html>Success</html>"
        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_handles_timeout(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(mock_client, "https://praca.by/test/")

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_http_error(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Error"))

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._request(mock_client, "https://praca.by/test/")

        assert result is None


class TestFetchVacancyDetails:
    @pytest.mark.asyncio
    async def test_fetches_and_parses_vacancy(
        self, parser: PracaByParser, sample_vacancy_html: str
    ) -> None:
        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_vacancy_html

            result = await parser.fetch_vacancy_details(mock_client, "12345")

        assert result is not None
        assert result.external_id == "12345"
        assert result.title == "Python Developer"

    @pytest.mark.asyncio
    async def test_returns_none_on_request_failure(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None

            result = await parser.fetch_vacancy_details(mock_client, "12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_parse_error(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = "<html></html>"

            with patch.object(parser, "_parse_vacancy_page", side_effect=Exception("Parse error")):
                result = await parser.fetch_vacancy_details(mock_client, "12345")

        assert result is None


class TestStreamVacancies:
    @pytest.mark.asyncio
    @freeze_time("2024-06-15")
    async def test_yields_vacancies_for_target_date(
        self, parser: PracaByParser, sample_vacancy_html: str
    ) -> None:
        search_html = """
        <article>
            <a class="vac-small__title-link" href="/vacancy/111/">Vacancy 1</a>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        """

        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [search_html, sample_vacancy_html, ""]

            results = []
            async for batch in parser.stream_vacancies(mock_client, date(2024, 6, 15)):
                results.extend(batch)

        assert len(results) == 1
        assert results[0].external_id == "111"

    @pytest.mark.asyncio
    @freeze_time("2024-06-15")
    async def test_skips_duplicate_vacancies(self, parser: PracaByParser) -> None:
        search_html_page1 = """
        <article>
            <a class="vac-small__title-link" href="/vacancy/111/">Vacancy 1</a>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        """
        search_html_page2 = """
        <article>
            <a class="vac-small__title-link" href="/vacancy/111/">Vacancy 1 duplicate</a>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        """
        vacancy_html = "<html><body><h1>Test Vacancy</h1></body></html>"

        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [
                search_html_page1,
                vacancy_html,
                search_html_page2,
                "",
            ]

            results = []
            async for batch in parser.stream_vacancies(mock_client, date(2024, 6, 15)):
                results.extend(batch)

        assert len(results) == 1

    @pytest.mark.asyncio
    @freeze_time("2024-06-15")
    async def test_stops_after_consecutive_empty_pages(self, parser: PracaByParser) -> None:
        target_date_html = """
        <article>
            <a class="vac-small__title-link" href="/vacancy/111/">Vacancy</a>
            <div class="vac-small__upped-time">сегодня</div>
        </article>
        """
        other_date_html = """
        <article>
            <a class="vac-small__title-link" href="/vacancy/222/">Other</a>
            <div class="vac-small__upped-time">вчера</div>
        </article>
        """
        vacancy_html = "<html><body><h1>Test</h1></body></html>"

        mock_client = AsyncMock()
        call_count = 0

        async def mock_response(*args: Any, **kwargs: Any) -> str | None:
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                return target_date_html
            elif call_count == 2:
                return vacancy_html
            else:
                return other_date_html

        with (
            patch.object(parser, "_request", mock_response),
            patch("src.core.config.praca_config.PRACA_MAX_PAGES", 100),
        ):
            results = []
            async for batch in parser.stream_vacancies(mock_client, date(2024, 6, 15)):
                results.extend(batch)

        assert len(results) == 1

    @pytest.mark.asyncio
    @freeze_time("2024-06-15")
    async def test_stops_on_empty_page(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = "<html><body></body></html>"

            results = []
            async for batch in parser.stream_vacancies(mock_client, date(2024, 6, 15)):
                results.extend(batch)

        assert len(results) == 0

    @pytest.mark.asyncio
    @freeze_time("2024-06-15")
    async def test_stops_on_request_failure(self, parser: PracaByParser) -> None:
        mock_client = AsyncMock()

        with patch.object(parser, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None

            results = []
            async for batch in parser.stream_vacancies(mock_client, date(2024, 6, 15)):
                results.extend(batch)

        assert len(results) == 0
