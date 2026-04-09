from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.epam.epam_parser import EpamParser


@pytest.fixture
def parser() -> EpamParser:
    return EpamParser(max_concurrent=2)


@pytest.fixture
def sample_vacancy_page_html() -> str:
    return """
    <html>
    <body>
        <h1 data-testid="job-details-banner-title">Senior Python Developer</h1>
        <div data-testid="upper-bar">
            <div data-testid="icon-bullet-container">
                <span data-testid="icon-bullet-item">Remote in</span>
                <span data-testid="icon-bullet-item">Poland: Warsaw</span>
            </div>
            <div data-testid="icon-bullet-container">
                <span data-testid="icon-bullet-item">Python</span>
                <span data-testid="icon-bullet-item">Django</span>
            </div>
        </div>
        <div data-testid="description-content">
            <div data-testid="rich-text">
                <p>We are looking for a Senior Python Developer</p>
            </div>
        </div>
        <div data-testid="accordion-section-container">
            <div data-testid="accordion-section-label-container">Responsibilities</div>
            <div data-testid="accordion-section-children-container">
                <p>Design and develop applications</p>
            </div>
        </div>
        <div data-testid="accordion-section-container">
            <div data-testid="accordion-section-label-container">Requirements</div>
            <div data-testid="accordion-section-children-container">
                <p>5+ years of experience in Python development</p>
            </div>
        </div>
        <div data-testid="accordion-section-container">
            <div data-testid="accordion-section-label-container">Nice to have</div>
            <div data-testid="accordion-section-children-container">
                <p>Experience with FastAPI</p>
            </div>
        </div>
        <div data-testid="accordion-section-container">
            <div data-testid="accordion-section-label-container">We offer/Benefits</div>
            <div data-testid="accordion-section-children-container">
                <p>Competitive salary</p>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_page_minimal_html() -> str:
    return """
    <html>
    <body>
        <h1>Junior Developer</h1>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_page_internship_html() -> str:
    return """
    <html>
    <body>
        <h1 data-testid="job-details-banner-title">Software Engineering Intern</h1>
        <div data-testid="description-content">
            <div data-testid="rich-text">
                <p>Join our internship program</p>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_html() -> str:
    return """
    <html>
    <body>
        <a data-testid="job-card-link" href="/en/vacancy/senior-python-developer-blt123abc456"></a>
        <a data-testid="job-card-link" href="/en/vacancy/java-developer-blt789def012"></a>
        <a data-testid="job-card-link" href="/en/vacancy/devops-engineer-blt345ghi678"></a>
        <button aria-label="next page"></button>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_last_html() -> str:
    return """
    <html>
    <body>
        <a data-testid="job-card-link" href="/en/vacancy/last-vacancy-bltlast123"></a>
        <button aria-label="next page" disabled></button>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_empty_html() -> str:
    return """
    <html>
    <body>
        <div>No vacancies found</div>
    </body>
    </html>
    """


def create_vacancy_result(external_id: str = "blt123", title: str = "Test") -> ParserVacancyResult:
    """Helper to create ParserVacancyResult for tests."""
    return ParserVacancyResult(
        external_id=external_id,
        title=title,
        description=None,
        company_name="EPAM Systems",
        company_external_id="epam",
        salary_from=None,
        salary_to=None,
        currency=None,
        city=None,
        address=None,
        experience=None,
        education=None,
        employment=None,
        schedule=None,
        is_remote=False,
        published_at=None,
        internship=False,
        created_at=None,
        vacancy_url="https://test.com",
        skills=[],
    )


class TestExtractExternalId:
    def test_extracts_blt_id(self, parser: EpamParser) -> None:
        slug = "senior-python-developer-blt123abc456def"
        result = parser._extract_external_id(slug)
        assert result == "blt123abc456def"

    def test_extracts_blt_id_at_start(self, parser: EpamParser) -> None:
        slug = "blt999xyz-developer"
        result = parser._extract_external_id(slug)
        assert result == "blt999xyz"

    def test_extracts_blt_id_case_insensitive(self, parser: EpamParser) -> None:
        slug = "developer-BLT789ABC123"
        result = parser._extract_external_id(slug)
        assert result == "BLT789ABC123"

    def test_returns_slug_when_no_blt_id(self, parser: EpamParser) -> None:
        slug = "some-random-slug-without-id"
        result = parser._extract_external_id(slug)
        assert result == slug

    def test_returns_empty_slug(self, parser: EpamParser) -> None:
        result = parser._extract_external_id("")
        assert result == ""


class TestExtractVacancyIdsFromList:
    def test_extracts_vacancy_refs(self, parser: EpamParser, sample_search_page_html: str) -> None:
        result = parser._extract_vacancy_ids_from_list(sample_search_page_html)

        assert len(result) == 3
        assert result[0]["external_id"] == "blt123abc456"
        assert result[0]["slug"] == "senior-python-developer-blt123abc456"
        assert "vacancy/senior-python-developer-blt123abc456" in result[0]["url"]

    def test_returns_empty_list_for_empty_page(
        self, parser: EpamParser, sample_search_page_empty_html: str
    ) -> None:
        result = parser._extract_vacancy_ids_from_list(sample_search_page_empty_html)
        assert len(result) == 0

    def test_skips_cards_without_href(self, parser: EpamParser) -> None:
        html = '<a data-testid="job-card-link"></a>'
        result = parser._extract_vacancy_ids_from_list(html)
        assert len(result) == 0

    def test_skips_cards_with_empty_href(self, parser: EpamParser) -> None:
        html = '<a data-testid="job-card-link" href=""></a>'
        result = parser._extract_vacancy_ids_from_list(html)
        assert len(result) == 0

    def test_skips_invalid_href_format(self, parser: EpamParser) -> None:
        html = '<a data-testid="job-card-link" href="/en/some-other-page"></a>'
        result = parser._extract_vacancy_ids_from_list(html)
        assert len(result) == 0


class TestHasNextPage:
    def test_returns_true_when_next_button_enabled(
        self, parser: EpamParser, sample_search_page_html: str
    ) -> None:
        result = parser._has_next_page(sample_search_page_html)
        assert result is True

    def test_returns_false_when_next_button_disabled(
        self, parser: EpamParser, sample_search_page_last_html: str
    ) -> None:
        result = parser._has_next_page(sample_search_page_last_html)
        assert result is False

    def test_returns_false_when_no_next_button(self, parser: EpamParser) -> None:
        html = "<html><body><div>No pagination</div></body></html>"
        result = parser._has_next_page(html)
        assert result is False

    def test_returns_false_for_empty_html(self, parser: EpamParser) -> None:
        result = parser._has_next_page("")
        assert result is False


class TestExtractTitle:
    def test_extracts_title_from_testid(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_title(tree)
        assert result == "Senior Python Developer"

    def test_extracts_title_from_h1_fallback(
        self, parser: EpamParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_minimal_html)
        result = parser._extract_title(tree)
        assert result == "Junior Developer"

    def test_returns_unknown_when_no_title(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser("<html><body></body></html>")
        result = parser._extract_title(tree)
        assert result == "Unknown Position"

    def test_strips_whitespace_from_title(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<h1 data-testid="job-details-banner-title">  Developer  </h1>'
        tree = HTMLParser(html)
        result = parser._extract_title(tree)
        assert result == "Developer"


class TestExtractDescription:
    def test_extracts_description_html(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_description(tree)

        assert result is not None
        assert "Senior Python Developer" in result

    def test_returns_none_when_no_description(
        self, parser: EpamParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_minimal_html)
        result = parser._extract_description(tree)
        assert result is None

    def test_returns_none_when_no_rich_text(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = '<div data-testid="description-content"><div>No rich text</div></div>'
        tree = HTMLParser(html)
        result = parser._extract_description(tree)
        assert result is None


class TestExtractLocation:
    def test_extracts_remote_and_countries(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_location(tree)

        assert result["is_remote"] is True
        assert result["address"] is not None or result["city"] is not None

    def test_returns_defaults_when_no_location(
        self, parser: EpamParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_minimal_html)
        result = parser._extract_location(tree)

        assert result["is_remote"] is False
        assert result["address"] is None
        assert result["city"] is None

    def test_detects_remote_keyword(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <div data-testid="upper-bar">
            <div data-testid="icon-bullet-container">
                <span data-testid="icon-bullet-item">Remote in</span>
                <span data-testid="icon-bullet-item">Ukraine</span>
            </div>
        </div>
        """
        tree = HTMLParser(html)
        result = parser._extract_location(tree)
        assert result["is_remote"] is True

    def test_extracts_country_from_link(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <div data-testid="upper-bar">
            <div data-testid="icon-bullet-container">
                <a data-testid="icon-bullet-link-item-link" href="/en/united-states-it-jobs">United States</a>
            </div>
        </div>
        """
        tree = HTMLParser(html)
        result = parser._extract_location(tree)
        assert result["address"] is not None
        assert "United States" in result["address"]

    def test_handles_none_href(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <div data-testid="upper-bar">
            <div data-testid="icon-bullet-container">
                <a data-testid="icon-bullet-link-item-link">No href</a>
            </div>
        </div>
        """
        tree = HTMLParser(html)
        result = parser._extract_location(tree)

        assert result["address"] == "No href"

    def test_extracts_city_from_colon_format(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <div data-testid="upper-bar">
            <div data-testid="icon-bullet-container">
                <span data-testid="icon-bullet-item">Hybrid in</span>
                <span data-testid="icon-bullet-item">Hungary: Budapest</span>
            </div>
        </div>
        """
        tree = HTMLParser(html)
        result = parser._extract_location(tree)
        assert result["address"] == "Hungary"
        assert result["city"] == "Budapest"


class TestExtractSection:
    def test_extracts_responsibilities_section(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_section(tree, "Responsibilities")

        assert result is not None
        assert "Design and develop" in result

    def test_extracts_requirements_section(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_section(tree, "Requirements")

        assert result is not None
        assert "experience" in result

    def test_extracts_nice_to_have_section(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_section(tree, "Nice to have")

        assert result is not None
        assert "FastAPI" in result

    def test_extracts_benefits_section(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_html)
        result = parser._extract_section(tree, "We offer/Benefits")

        assert result is not None
        assert "salary" in result

    def test_returns_none_for_missing_section(
        self, parser: EpamParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(sample_vacancy_page_minimal_html)
        result = parser._extract_section(tree, "Responsibilities")
        assert result is None

    def test_case_insensitive_match(self, parser: EpamParser) -> None:
        from selectolax.parser import HTMLParser

        html = """
        <div data-testid="accordion-section-container">
            <div data-testid="accordion-section-label-container">REQUIREMENTS</div>
            <div data-testid="accordion-section-children-container">
                <p>Content here</p>
            </div>
        </div>
        """
        tree = HTMLParser(html)
        result = parser._extract_section(tree, "requirements")
        assert result is not None


class TestBuildFullDescription:
    def test_builds_full_description_with_all_parts(self, parser: EpamParser) -> None:
        result = parser._build_full_description(
            description="<p>Main description</p>",
            responsibilities="<p>Do stuff</p>",
            requirements="<p>Know things</p>",
            nice_to_have="<p>Extra skills</p>",
            benefits="<p>Good salary</p>",
        )

        assert "<p>Main description</p>" in result
        assert "<h3>Responsibilities</h3>" in result
        assert "<h3>Requirements</h3>" in result
        assert "<h3>Nice to have</h3>" in result
        assert "<h3>Benefits</h3>" in result

    def test_builds_description_with_partial_data(self, parser: EpamParser) -> None:
        result = parser._build_full_description(
            description="<p>Only description</p>",
            responsibilities=None,
            requirements="<p>Some requirements</p>",
            nice_to_have=None,
            benefits=None,
        )

        assert "<p>Only description</p>" in result
        assert "<h3>Requirements</h3>" in result
        assert "<h3>Responsibilities</h3>" not in result
        assert "<h3>Nice to have</h3>" not in result
        assert "<h3>Benefits</h3>" not in result

    def test_returns_empty_string_when_all_none(self, parser: EpamParser) -> None:
        result = parser._build_full_description(
            description=None,
            responsibilities=None,
            requirements=None,
            nice_to_have=None,
            benefits=None,
        )
        assert result == ""

    def test_joins_parts_with_newline(self, parser: EpamParser) -> None:
        result = parser._build_full_description(
            description="<p>Desc</p>",
            responsibilities="<p>Resp</p>",
            requirements=None,
            nice_to_have=None,
            benefits=None,
        )
        assert "\n" in result


class TestParseVacancyPage:
    def test_parses_full_vacancy(self, parser: EpamParser, sample_vacancy_page_html: str) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_html, "blt123abc456", "https://careers.epam.com/en/vacancy/test"
        )

        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "blt123abc456"
        assert result.title == "Senior Python Developer"
        assert result.company_name == "EPAM Systems"
        assert result.company_external_id == "epam"

        assert result.internship is None
        assert result.vacancy_url == "https://careers.epam.com/en/vacancy/test"
        assert result.experience is not None

    def test_parses_minimal_vacancy(
        self, parser: EpamParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_minimal_html,
            "blt999",
            "https://careers.epam.com/en/vacancy/minimal",
        )

        assert result.title == "Junior Developer"
        assert result.is_remote is False
        assert len(result.skills) == 0
        assert result.description == ""

    def test_parses_internship_vacancy(
        self, parser: EpamParser, sample_vacancy_page_internship_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_internship_html,
            "blt_intern",
            "https://careers.epam.com/en/vacancy/intern",
        )

        assert result.internship is None

    def test_always_sets_epam_company(self, parser: EpamParser) -> None:
        result = parser._parse_vacancy_page("<html><body></body></html>", "test", "url")
        assert result.company_name == "EPAM Systems"
        assert result.company_external_id == "epam"

    def test_salary_fields_are_none(self, parser: EpamParser) -> None:
        result = parser._parse_vacancy_page("<html><body></body></html>", "test", "url")
        assert result.salary_from is None
        assert result.salary_to is None
        assert result.currency is None


class TestFetchPageWithJs:
    @pytest.mark.asyncio
    async def test_returns_html_on_success(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await parser._fetch_page_with_js("https://test.com", "[data-testid='test']")

        assert result == "<html>Success</html>"
        mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_timeout(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=[PlaywrightTimeout("timeout"), None])
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 3),
        ):
            result = await parser._fetch_page_with_js("https://test.com", "[data-testid='test']")

        assert result == "<html>Success</html>"

    @pytest.mark.asyncio
    async def test_returns_none_after_max_retries(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 2),
        ):
            result = await parser._fetch_page_with_js("https://test.com", "[data-testid='test']")

        assert result is None
        mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_generic_exception(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=[Exception("Network error"), None])
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 3),
        ):
            result = await parser._fetch_page_with_js("https://test.com", "[data-testid='test']")

        assert result == "<html>Success</html>"

    @pytest.mark.asyncio
    async def test_always_closes_page(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Fatal error"))
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 1),
        ):
            result = await parser._fetch_page_with_js("https://test.com", "[data-testid='test']")

        assert result is None
        mock_page.close.assert_called_once()


class TestFetchStaticPage:
    @pytest.mark.asyncio
    async def test_returns_html_on_200(self, parser: EpamParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await parser._fetch_static_page("https://test.com")

        assert result == "<html>Success</html>"

    @pytest.mark.asyncio
    async def test_backs_off_on_429(self, parser: EpamParser) -> None:
        mock_response_429 = MagicMock()
        mock_response_429.status = 429

        mock_response_200 = MagicMock()
        mock_response_200.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=[mock_response_429, mock_response_200])
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("src.core.config.epam_config.EPAM_RETRIES", 3),
        ):
            result = await parser._fetch_static_page("https://test.com")

        assert result == "<html>Success</html>"

        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert any(s >= 30 for s in sleep_calls)

    @pytest.mark.asyncio
    async def test_returns_none_on_bad_status(self, parser: EpamParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 500

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 1),
        ):
            result = await parser._fetch_static_page("https://test.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_none_response(self, parser: EpamParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=None)
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_RETRIES", 1),
        ):
            result = await parser._fetch_static_page("https://test.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_timeout_on_wait_for_selector(self, parser: EpamParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        mock_page.content = AsyncMock(return_value="<html>Success</html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await parser._fetch_static_page("https://test.com")

        assert result == "<html>Success</html>"


class TestFetchVacancyDetails:
    @pytest.mark.asyncio
    async def test_fetches_and_parses_vacancy(
        self, parser: EpamParser, sample_vacancy_page_html: str
    ) -> None:
        with patch.object(parser, "_fetch_static_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = sample_vacancy_page_html

            result = await parser._fetch_vacancy_details(
                "https://careers.epam.com/en/vacancy/test", "blt123"
            )

        assert result is not None
        assert result.external_id == "blt123"
        assert result.title == "Senior Python Developer"

    @pytest.mark.asyncio
    async def test_returns_none_on_fetch_failure(self, parser: EpamParser) -> None:
        with patch.object(parser, "_fetch_static_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None

            result = await parser._fetch_vacancy_details(
                "https://careers.epam.com/en/vacancy/test", "blt123"
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_parse_error(self, parser: EpamParser) -> None:
        with (
            patch.object(parser, "_fetch_static_page", new_callable=AsyncMock) as mock_fetch,
            patch.object(parser, "_parse_vacancy_page", side_effect=Exception("Parse error")),
        ):
            mock_fetch.return_value = "<html></html>"

            result = await parser._fetch_vacancy_details(
                "https://careers.epam.com/en/vacancy/test", "blt123"
            )

        assert result is None


class TestFetchVacanciesBatch:
    @pytest.mark.asyncio
    async def test_fetches_batch_of_vacancies(self, parser: EpamParser) -> None:
        refs = [
            {"url": "https://test.com/1", "external_id": "blt1"},
            {"url": "https://test.com/2", "external_id": "blt2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = create_vacancy_result()

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 2
        assert mock_fetch.call_count == 2

    @pytest.mark.asyncio
    async def test_filters_none_results(self, parser: EpamParser) -> None:
        refs = [
            {"url": "https://test.com/1", "external_id": "blt1"},
            {"url": "https://test.com/2", "external_id": "blt2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [create_vacancy_result(), None]

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_handles_exceptions_in_batch(self, parser: EpamParser) -> None:
        refs = [
            {"url": "https://test.com/1", "external_id": "blt1"},
            {"url": "https://test.com/2", "external_id": "blt2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [create_vacancy_result(), Exception("Network error")]

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty_refs(self, parser: EpamParser) -> None:
        results = await parser._fetch_vacancies_batch([])
        assert len(results) == 0


class TestStreamVacancies:
    @pytest.mark.asyncio
    async def test_streams_vacancies_from_multiple_pages(
        self,
        parser: EpamParser,
        sample_search_page_html: str,
        sample_search_page_last_html: str,
    ) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch_list,
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_MAX_PAGES", 10),
        ):
            mock_fetch_list.side_effect = [sample_search_page_html, sample_search_page_last_html]
            mock_fetch_batch.return_value = [create_vacancy_result()]

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert mock_fetch_batch.call_count == 2

    @pytest.mark.asyncio
    async def test_stops_on_empty_page(
        self, parser: EpamParser, sample_search_page_empty_html: str
    ) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch,
            patch.object(parser, "close", new_callable=AsyncMock),
        ):
            mock_fetch.return_value = sample_search_page_empty_html

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_stops_on_fetch_failure(self, parser: EpamParser) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch,
            patch.object(parser, "close", new_callable=AsyncMock),
        ):
            mock_fetch.return_value = None

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_skips_duplicate_vacancies(
        self, parser: EpamParser, sample_search_page_html: str
    ) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch_list,
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_MAX_PAGES", 2),
        ):
            mock_fetch_list.side_effect = [sample_search_page_html, sample_search_page_html]
            mock_fetch_batch.return_value = [create_vacancy_result()]

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert mock_fetch_batch.call_count == 1

    @pytest.mark.asyncio
    async def test_stops_at_max_pages(
        self, parser: EpamParser, sample_search_page_html: str
    ) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch_list,
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "_extract_vacancy_ids_from_list") as mock_extract,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_MAX_PAGES", 3),
        ):
            mock_fetch_list.return_value = sample_search_page_html
            mock_extract.side_effect = [
                [{"external_id": f"blt{i}", "slug": f"slug{i}", "url": f"url{i}"}] for i in range(3)
            ]
            mock_fetch_batch.return_value = [create_vacancy_result()]

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert mock_fetch_list.call_count == 3

    @pytest.mark.asyncio
    async def test_stops_when_no_next_page(
        self, parser: EpamParser, sample_search_page_last_html: str
    ) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch_list,
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.epam_config.EPAM_MAX_PAGES", 10),
        ):
            mock_fetch_list.return_value = sample_search_page_last_html
            mock_fetch_batch.return_value = [create_vacancy_result()]

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert mock_fetch_list.call_count == 1

    @pytest.mark.asyncio
    async def test_closes_browser_on_completion(self, parser: EpamParser) -> None:
        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch,
            patch.object(parser, "close", new_callable=AsyncMock) as mock_close,
        ):
            mock_fetch.return_value = None

            async for _ in parser.stream_vacancies():
                pass

        mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_yields_batches_correctly(
        self, parser: EpamParser, sample_search_page_last_html: str
    ) -> None:
        vacancy1 = create_vacancy_result("blt1", "Vacancy 1")
        vacancy2 = create_vacancy_result("blt2", "Vacancy 2")

        with (
            patch.object(parser, "_fetch_page_with_js", new_callable=AsyncMock) as mock_fetch_list,
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
        ):
            mock_fetch_list.return_value = sample_search_page_last_html
            mock_fetch_batch.return_value = [vacancy1, vacancy2]

            batches = []
            async for batch in parser.stream_vacancies():
                batches.append(batch)

        assert len(batches) == 1
        assert len(batches[0]) == 2


class TestClose:
    @pytest.mark.asyncio
    async def test_closes_all_resources(self, parser: EpamParser) -> None:
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()

        parser._context = mock_context
        parser._browser = mock_browser
        parser._playwright = mock_playwright

        await parser.close()

        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()

        assert parser._context is None
        assert parser._browser is None
        assert parser._playwright is None

    @pytest.mark.asyncio
    async def test_handles_already_closed(self, parser: EpamParser) -> None:
        parser._context = None
        parser._browser = None
        parser._playwright = None

        await parser.close()

    @pytest.mark.asyncio
    async def test_partial_close(self, parser: EpamParser) -> None:
        mock_context = AsyncMock()
        parser._context = mock_context
        parser._browser = None
        parser._playwright = None

        await parser.close()

        mock_context.close.assert_called_once()
        assert parser._context is None


class TestEnsureBrowser:
    @pytest.mark.asyncio
    async def test_creates_browser_on_first_call(self, parser: EpamParser) -> None:
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        with patch("src.parsers.epam.epam_parser.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            result = await parser._ensure_browser()

        assert result == mock_context
        assert parser._browser == mock_browser
        assert parser._context == mock_context

    @pytest.mark.asyncio
    async def test_reuses_existing_browser(self, parser: EpamParser) -> None:
        existing_context = AsyncMock()
        parser._browser = AsyncMock()
        parser._context = existing_context

        result = await parser._ensure_browser()

        assert result == existing_context

    @pytest.mark.asyncio
    async def test_recreates_if_browser_none(self, parser: EpamParser) -> None:
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        parser._browser = None
        parser._context = AsyncMock()

        with patch("src.parsers.epam.epam_parser.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            result = await parser._ensure_browser()

        assert result == mock_context
        assert parser._browser == mock_browser


class TestCreatePage:
    @pytest.mark.asyncio
    async def test_creates_new_page(self, parser: EpamParser) -> None:
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        with patch.object(parser, "_ensure_browser", return_value=mock_context):
            result = await parser._create_page()

        assert result == mock_page
        mock_context.new_page.assert_called_once()
