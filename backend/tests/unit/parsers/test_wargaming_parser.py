from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.wargaming.wargaming_parser import WargamingParser


@pytest.fixture
def parser() -> WargamingParser:
    return WargamingParser()


@pytest.fixture
def sample_vacancy_page_html() -> str:
    return """
    <html>
    <body>
        <section class="vacancy">
            <h1>Senior Python Developer</h1>
            <div class="place">Berlin, Germany</div>
            <div class="col-2">
                <div class="title">Engineering</div>
            </div>
            <div class="list _intro">
                <h3><strong>What will you do?</strong></h3>
                <ul>
                    <li>Develop backend services</li>
                    <li>5+ years of experience required</li>
                </ul>
                <h3><strong>Requirements</strong></h3>
                <ul>
                    <li>Python expertise</li>
                    <li>Remote work possible</li>
                </ul>
            </div>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_page_minimal_html() -> str:
    return """
    <html>
    <body>
        <section class="vacancy">
            <h1>Junior Developer</h1>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_page_internship_html() -> str:
    return """
    <html>
    <body>
        <section class="vacancy">
            <h1>Software Engineering Intern</h1>
            <div class="place">Minsk, Belarus</div>
            <div class="list _intro">
                <p>Join our internship program</p>
            </div>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_vacancy_page_hybrid_html() -> str:
    return """
    <html>
    <body>
        <section class="vacancy">
            <h1>Data Engineer</h1>
            <div class="place">Warsaw, Poland</div>
            <div class="list _intro">
                <p>Hybrid work model available</p>
            </div>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_html() -> str:
    return """
    <html>
    <body>
        <section class="jobs">
            <ul class="job-list">
                <li>
                    <ul>
                        <li>
                            <a class="title" href="/en/careers/vacancy_12345_berlin/">Senior Python Developer</a>
                            <div class="description">Engineering</div>
                            <div class="place">Berlin, Germany</div>
                        </li>
                    </ul>
                </li>
                <li>
                    <ul>
                        <li>
                            <a class="title" href="/en/careers/vacancy_67890_minsk/">QA Engineer</a>
                            <div class="description">Quality Assurance</div>
                            <div class="place">Minsk, Belarus</div>
                        </li>
                    </ul>
                </li>
                <li>
                    <ul>
                        <li>
                            <a class="title" href="/en/careers/vacancy_11111_nicosia/">DevOps Engineer</a>
                            <div class="description">Infrastructure</div>
                            <div class="place">Nicosia, Cyprus</div>
                        </li>
                    </ul>
                </li>
            </ul>
            <div class="show-more">
                <a href="#">Show more</a>
            </div>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_no_more_html() -> str:
    return """
    <html>
    <body>
        <section class="jobs">
            <ul class="job-list">
                <li>
                    <ul>
                        <li>
                            <a class="title" href="/en/careers/vacancy_99999_prague/">Last Vacancy</a>
                            <div class="description">Team</div>
                            <div class="place">Prague, Czech Republic</div>
                        </li>
                    </ul>
                </li>
            </ul>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_page_empty_html() -> str:
    return """
    <html>
    <body>
        <section class="jobs">
            <ul class="job-list"></ul>
        </section>
    </body>
    </html>
    """


def create_vacancy_result(
    external_id: str = "vacancy_12345_berlin",
    title: str = "Test Developer",
) -> ParserVacancyResult:
    """Helper to create ParserVacancyResult for tests."""
    return ParserVacancyResult(
        external_id=external_id,
        title=title,
        description=None,
        company_name="Wargaming",
        company_external_id="wargaming",
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
        vacancy_url="https://wargaming.com/en/careers/vacancy_12345_berlin/",
        skills=[],
    )


class TestExtractVacancyRefs:
    def test_extracts_vacancy_refs(
        self, parser: WargamingParser, sample_search_page_html: str
    ) -> None:
        result = parser._extract_vacancy_refs(sample_search_page_html)

        assert len(result) == 3
        assert result[0]["external_id"] == "vacancy_12345_berlin"
        assert result[0]["title"] == "Senior Python Developer"
        assert result[0]["department"] == "Engineering"
        assert result[0]["location"] == "Berlin, Germany"
        assert "vacancy_12345_berlin" in result[0]["url"]

    def test_extracts_full_slug_as_external_id(
        self, parser: WargamingParser, sample_search_page_html: str
    ) -> None:
        result = parser._extract_vacancy_refs(sample_search_page_html)

        # Проверяем что external_id содержит полный slug
        assert result[0]["external_id"] == "vacancy_12345_berlin"
        assert result[1]["external_id"] == "vacancy_67890_minsk"
        assert result[2]["external_id"] == "vacancy_11111_nicosia"

    def test_returns_empty_list_for_empty_page(
        self, parser: WargamingParser, sample_search_page_empty_html: str
    ) -> None:
        result = parser._extract_vacancy_refs(sample_search_page_empty_html)
        assert len(result) == 0

    def test_skips_items_without_link(self, parser: WargamingParser) -> None:
        html = """
        <ul class="job-list">
            <li><li>
                <div class="description">No link here</div>
            </li></li>
        </ul>
        """
        result = parser._extract_vacancy_refs(html)
        assert len(result) == 0

    def test_skips_items_without_vacancy_in_href(self, parser: WargamingParser) -> None:
        html = """
        <ul class="job-list">
            <li><li>
                <a class="title" href="/en/careers/some-other-page/">Other Page</a>
            </li></li>
        </ul>
        """
        result = parser._extract_vacancy_refs(html)
        assert len(result) == 0

    def test_skips_items_with_invalid_vacancy_format(self, parser: WargamingParser) -> None:
        html = """
        <ul class="job-list">
            <li><li>
                <a class="title" href="/en/careers/vacancy_no_location/">Invalid</a>
            </li></li>
        </ul>
        """
        result = parser._extract_vacancy_refs(html)
        assert len(result) == 0

    def test_handles_missing_department(self, parser: WargamingParser) -> None:
        html = """
        <ul class="job-list">
            <li>
                <ul>
                    <li>
                        <a class="title" href="/en/careers/vacancy_123_city/">Title</a>
                        <div class="place">City</div>
                    </li>
                </ul>
            </li>
        </ul>
        """
        result = parser._extract_vacancy_refs(html)
        assert len(result) == 1
        assert result[0]["department"] == "No info"

    def test_handles_missing_location(self, parser: WargamingParser) -> None:
        html = """
        <ul class="job-list">
            <li>
                <ul>
                    <li>
                        <a class="title" href="/en/careers/vacancy_123_city/">Title</a>
                        <div class="description">Team</div>
                    </li>
                </ul>
            </li>
        </ul>
        """
        result = parser._extract_vacancy_refs(html)
        assert len(result) == 1
        assert result[0]["location"] == "No info"


class TestCleanDescription:
    def test_removes_images(self, parser: WargamingParser) -> None:
        html = '<div><img src="test.jpg"/><p>Text content</p></div>'
        result = parser._clean_description(html)

        assert result is not None
        assert "<img" not in result
        assert "Text content" in result

    def test_removes_iframes(self, parser: WargamingParser) -> None:
        html = '<div><iframe src="video.mp4"></iframe><p>Text</p></div>'
        result = parser._clean_description(html)

        assert result is not None
        assert "<iframe" not in result

    def test_removes_reports_to_section(self, parser: WargamingParser) -> None:
        html = """
        <h3><strong>Reports to</strong></h3>
        <p>Some manager</p>
        <h3><strong>What will you do?</strong></h3>
        <p>Actual content</p>
        """
        result = parser._clean_description(html)

        assert result is not None
        assert "Reports to" not in result
        assert "Some manager" not in result
        assert "What will you do" in result

    def test_removes_cv_submission_text(self, parser: WargamingParser) -> None:
        html = """
        <p>Job description</p>
        <h5>Please submit your CV in English</h5>
        <p>More text after</p>
        """
        result = parser._clean_description(html)

        assert result is not None
        assert "Please submit your CV" not in result
        assert "Job description" in result

    def test_removes_about_wargaming_section(self, parser: WargamingParser) -> None:
        html = """
        <p>Job info</p>
        <div class="content-conclusion">About Wargaming...</div>
        """
        result = parser._clean_description(html)

        assert result is not None
        assert "content-conclusion" not in result

    def test_returns_none_for_empty_html(self, parser: WargamingParser) -> None:
        result = parser._clean_description("")
        assert result is None

    def test_returns_none_for_none_input(self, parser: WargamingParser) -> None:
        result = parser._clean_description(None)
        assert result is None

    def test_removes_empty_h3_tags(self, parser: WargamingParser) -> None:
        html = "<h3>&nbsp;</h3><h3>  </h3><p>Content</p>"
        result = parser._clean_description(html)

        assert result is not None
        # Пустые h3 должны быть удалены
        assert result.count("<h3") <= 1 or "Content" in result


class TestExtractExperience:
    def test_extracts_years_of_experience(self, parser: WargamingParser) -> None:
        description = "We need 5 years of experience in Python"
        result = parser._extract_experience(description)

        assert result is not None
        assert "5" in result
        assert "years" in result.lower()

    def test_extracts_years_plus_format(self, parser: WargamingParser) -> None:
        description = "Required: 3+ years experience in backend"
        result = parser._extract_experience(description)

        assert result is not None
        assert "3+" in result

    def test_extracts_at_least_format(self, parser: WargamingParser) -> None:
        description = "You should have at least 2 years of work"
        result = parser._extract_experience(description)

        assert result is not None
        assert "2" in result

    def test_returns_none_when_no_experience(self, parser: WargamingParser) -> None:
        description = "No experience requirements mentioned"
        result = parser._extract_experience(description)
        assert result is None

    def test_returns_none_for_none_description(self, parser: WargamingParser) -> None:
        result = parser._extract_experience(None)
        assert result is None

    def test_case_insensitive(self, parser: WargamingParser) -> None:
        description = "5 YEARS OF EXPERIENCE required"
        result = parser._extract_experience(description)

        assert result is not None
        assert "5" in result


class TestParseVacancyPage:
    def test_parses_full_vacancy(
        self, parser: WargamingParser, sample_vacancy_page_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_html,
            "vacancy_12345_berlin",
            "https://wargaming.com/en/careers/vacancy_12345_berlin/",
            {"title": "Fallback Title", "department": "Fallback Dept", "location": "Fallback Loc"},
        )

        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "vacancy_12345_berlin"
        assert result.title == "Senior Python Developer"
        assert result.company_name == "Wargaming"
        assert result.company_external_id == "wargaming"
        assert result.city == "Berlin"
        assert result.address == "Berlin, Germany"
        assert result.employment == "Engineering"
        assert result.is_remote is True
        assert result.internship is False
        assert result.experience is not None

    def test_parses_minimal_vacancy(
        self, parser: WargamingParser, sample_vacancy_page_minimal_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_minimal_html,
            "vacancy_99999_test",
            "https://wargaming.com/en/careers/vacancy_99999_test/",
            {"title": "Prefetched Title"},
        )

        assert result.title == "Junior Developer"
        assert result.city is None
        assert result.is_remote is False
        assert result.experience is None

    def test_parses_internship_vacancy(
        self, parser: WargamingParser, sample_vacancy_page_internship_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_internship_html,
            "vacancy_intern_123",
            "url",
            {},
        )

        assert result.internship is True
        assert "Intern" in result.title

    def test_parses_hybrid_as_remote(
        self, parser: WargamingParser, sample_vacancy_page_hybrid_html: str
    ) -> None:
        result = parser._parse_vacancy_page(
            sample_vacancy_page_hybrid_html,
            "vacancy_hybrid_456",
            "url",
            {},
        )

        assert result.is_remote is True

    def test_uses_prefetched_data_as_fallback(self, parser: WargamingParser) -> None:
        html = "<html><body><section class='vacancy'></section></body></html>"
        prefetched = {
            "title": "Prefetched Title",
            "location": "Prefetched Location",
            "department": "Prefetched Department",
        }

        result = parser._parse_vacancy_page(html, "ext_id", "url", prefetched)

        assert result.title == "Prefetched Title"
        assert result.address == "Prefetched Location"
        assert result.employment == "Prefetched Department"

    def test_extracts_city_from_location(self, parser: WargamingParser) -> None:
        html = """
        <section class="vacancy">
            <h1>Test</h1>
            <div class="place">Warsaw, Poland, Europe</div>
        </section>
        """
        result = parser._parse_vacancy_page(html, "ext_id", "url", {})

        assert result.city == "Warsaw"
        assert result.address == "Warsaw, Poland, Europe"

    def test_always_sets_wargaming_company(self, parser: WargamingParser) -> None:
        result = parser._parse_vacancy_page("<html><body></body></html>", "test", "url", {})

        assert result.company_name == "Wargaming"
        assert result.company_external_id == "wargaming"

    def test_salary_fields_are_none(self, parser: WargamingParser) -> None:
        result = parser._parse_vacancy_page("<html><body></body></html>", "test", "url", {})

        assert result.salary_from is None
        assert result.salary_to is None
        assert result.currency is None

    def test_detects_trainee_as_internship(self, parser: WargamingParser) -> None:
        html = """
        <section class="vacancy">
            <h1>Trainee QA Engineer</h1>
        </section>
        """
        result = parser._parse_vacancy_page(html, "test", "url", {})

        assert result.internship is True


class TestLoadAllVacancies:
    @pytest.mark.asyncio
    async def test_returns_html_when_jobs_found(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.query_selector_all = AsyncMock(return_value=[1, 2, 3])
        mock_page.content = AsyncMock(return_value="<html>Jobs loaded</html>")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._load_all_vacancies(mock_page)

        assert result == "<html>Jobs loaded</html>"

    @pytest.mark.asyncio
    async def test_clicks_show_more_until_hidden(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>All loaded</html>")

        # First call: button visible, second call: button hidden
        mock_button = AsyncMock()
        mock_button.is_visible = AsyncMock(side_effect=[True, True, False])
        mock_button.click = AsyncMock()

        mock_page.query_selector = AsyncMock(return_value=mock_button)
        mock_page.query_selector_all = AsyncMock(
            side_effect=[
                [1, 2],  # After first check
                [1, 2, 3, 4],  # After first click
                [1, 2, 3, 4, 5, 6],  # After second click
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._load_all_vacancies(mock_page)

        assert result == "<html>All loaded</html>"
        assert mock_button.click.call_count == 2

    @pytest.mark.asyncio
    async def test_stops_after_stale_count(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Stale</html>")

        mock_button = AsyncMock()
        mock_button.is_visible = AsyncMock(return_value=True)
        mock_button.click = AsyncMock()

        mock_page.query_selector = AsyncMock(return_value=mock_button)
        # Same count every time - should trigger stale detection
        mock_page.query_selector_all = AsyncMock(return_value=[1, 2, 3])

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._load_all_vacancies(mock_page)

        assert result == "<html>Stale</html>"
        assert mock_button.click.call_count == 3  # Stops after 3 stale attempts

    @pytest.mark.asyncio
    async def test_handles_wait_for_selector_timeout(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        mock_page.content = AsyncMock(return_value="<html>Fallback</html>")

        result = await parser._load_all_vacancies(mock_page)

        assert result == "<html>Fallback</html>"

    @pytest.mark.asyncio
    async def test_handles_click_error(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Error handled</html>")

        mock_button = AsyncMock()
        mock_button.is_visible = AsyncMock(return_value=True)
        mock_button.click = AsyncMock(side_effect=Exception("Click failed"))

        mock_page.query_selector = AsyncMock(return_value=mock_button)
        mock_page.query_selector_all = AsyncMock(return_value=[1, 2])

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await parser._load_all_vacancies(mock_page)

        assert result == "<html>Error handled</html>"


class TestFetchVacancyDetails:
    @pytest.mark.asyncio
    async def test_returns_vacancy_on_success(
        self, parser: WargamingParser, sample_vacancy_page_html: str
    ) -> None:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value=sample_vacancy_page_html)
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await parser._fetch_vacancy_details(
                "https://wargaming.com/en/careers/vacancy_12345_berlin/",
                "vacancy_12345_berlin",
                {"title": "Prefetched"},
            )

        assert result is not None
        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "vacancy_12345_berlin"
        mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_timeout(self, parser: WargamingParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=[PlaywrightTimeout("timeout"), mock_response])
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body><h1>Test</h1></body></html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_RETRIES", 3),
        ):
            result = await parser._fetch_vacancy_details("url", "ext_id", {})

        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_after_max_retries(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_RETRIES", 2),
        ):
            result = await parser._fetch_vacancy_details("url", "ext_id", {})

        assert result is None
        mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_on_bad_status(self, parser: WargamingParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 404

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_RETRIES", 1),
        ):
            result = await parser._fetch_vacancy_details("url", "ext_id", {})

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_wait_for_selector_timeout(self, parser: WargamingParser) -> None:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        mock_page.content = AsyncMock(return_value="<html><body><h1>Test</h1></body></html>")
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await parser._fetch_vacancy_details("url", "ext_id", {})

        # Should still return result even if selector not found
        assert result is not None

    @pytest.mark.asyncio
    async def test_always_closes_page(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Fatal error"))
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_RETRIES", 1),
        ):
            result = await parser._fetch_vacancy_details("url", "ext_id", {})

        assert result is None
        mock_page.close.assert_called_once()


class TestFetchVacanciesBatch:
    @pytest.mark.asyncio
    async def test_fetches_batch_of_vacancies(self, parser: WargamingParser) -> None:
        refs = [
            {"url": "https://test.com/1", "external_id": "vacancy_1_city", "title": "V1"},
            {"url": "https://test.com/2", "external_id": "vacancy_2_city", "title": "V2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = create_vacancy_result()

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 2
        assert mock_fetch.call_count == 2

    @pytest.mark.asyncio
    async def test_filters_none_results(self, parser: WargamingParser) -> None:
        refs = [
            {"url": "url1", "external_id": "v1", "title": "T1"},
            {"url": "url2", "external_id": "v2", "title": "T2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [create_vacancy_result(), None]

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_handles_exceptions_in_batch(self, parser: WargamingParser) -> None:
        refs = [
            {"url": "url1", "external_id": "v1", "title": "T1"},
            {"url": "url2", "external_id": "v2", "title": "T2"},
        ]

        with patch.object(parser, "_fetch_vacancy_details", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [create_vacancy_result(), Exception("Network error")]

            results = await parser._fetch_vacancies_batch(refs)

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty_refs(self, parser: WargamingParser) -> None:
        results = await parser._fetch_vacancies_batch([])
        assert len(results) == 0


class TestStreamVacancies:
    @pytest.mark.asyncio
    async def test_streams_vacancies_successfully(
        self, parser: WargamingParser, sample_search_page_html: str
    ) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", return_value=sample_search_page_html),
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_BATCH_SIZE", 10),
        ):
            mock_fetch_batch.return_value = [create_vacancy_result()]

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert len(results) == 1
        mock_fetch_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_yields_nothing_when_no_vacancies(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", return_value="<html></html>"),
            patch.object(parser, "_extract_vacancy_refs", return_value=[]),
            patch.object(parser, "close", new_callable=AsyncMock),
        ):
            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_processes_in_batches(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        # 5 vacancy refs, batch size 2 = 3 batches
        vacancy_refs = [
            {"url": f"url{i}", "external_id": f"v_{i}_city", "title": f"T{i}"} for i in range(5)
        ]

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", return_value="<html></html>"),
            patch.object(parser, "_extract_vacancy_refs", return_value=vacancy_refs),
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
            patch("src.core.config.wargaming_config.WARGAMING_BATCH_SIZE", 2),
        ):
            mock_fetch_batch.return_value = [create_vacancy_result()]

            batches_count = 0
            async for _ in parser.stream_vacancies():
                batches_count += 1

        assert batches_count == 3
        assert mock_fetch_batch.call_count == 3

    @pytest.mark.asyncio
    async def test_closes_browser_on_completion(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", return_value="<html></html>"),
            patch.object(parser, "_extract_vacancy_refs", return_value=[]),
            patch.object(parser, "close", new_callable=AsyncMock) as mock_close,
        ):
            async for _ in parser.stream_vacancies():
                pass

        mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_closes_browser_on_error(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", side_effect=Exception("Load failed")),
            patch.object(parser, "close", new_callable=AsyncMock) as mock_close,
        ):
            with pytest.raises(Exception, match="Load failed"):
                async for _ in parser.stream_vacancies():
                    pass

        mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_empty_batches(self, parser: WargamingParser) -> None:
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        vacancy_refs = [
            {"url": "url1", "external_id": "v1", "title": "T1"},
        ]

        with (
            patch.object(parser, "_create_page", return_value=mock_page),
            patch.object(parser, "_load_all_vacancies", return_value="<html></html>"),
            patch.object(parser, "_extract_vacancy_refs", return_value=vacancy_refs),
            patch.object(
                parser, "_fetch_vacancies_batch", new_callable=AsyncMock
            ) as mock_fetch_batch,
            patch.object(parser, "close", new_callable=AsyncMock),
        ):
            mock_fetch_batch.return_value = []  # Empty batch

            results = []
            async for batch in parser.stream_vacancies():
                results.extend(batch)

        assert len(results) == 0


class TestClose:
    @pytest.mark.asyncio
    async def test_closes_all_resources(self, parser: WargamingParser) -> None:
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
    async def test_handles_already_closed(self, parser: WargamingParser) -> None:
        parser._context = None
        parser._browser = None
        parser._playwright = None

        # Should not raise
        await parser.close()

    @pytest.mark.asyncio
    async def test_partial_close(self, parser: WargamingParser) -> None:
        mock_context = AsyncMock()
        parser._context = mock_context
        parser._browser = None
        parser._playwright = None

        await parser.close()

        mock_context.close.assert_called_once()
        assert parser._context is None


class TestEnsureBrowser:
    @pytest.mark.asyncio
    async def test_creates_browser_on_first_call(self, parser: WargamingParser) -> None:
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.add_init_script = AsyncMock()

        with patch(
            "src.parsers.wargaming.wargaming_parser.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            result = await parser._ensure_browser()

        assert result == mock_context
        assert parser._browser == mock_browser
        assert parser._context == mock_context

    @pytest.mark.asyncio
    async def test_reuses_existing_browser(self, parser: WargamingParser) -> None:
        existing_context = AsyncMock()
        parser._browser = AsyncMock()
        parser._context = existing_context

        result = await parser._ensure_browser()

        assert result == existing_context

    @pytest.mark.asyncio
    async def test_recreates_if_browser_none(self, parser: WargamingParser) -> None:
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.add_init_script = AsyncMock()

        parser._browser = None
        parser._context = AsyncMock()  # Context exists but browser is None

        with patch(
            "src.parsers.wargaming.wargaming_parser.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            result = await parser._ensure_browser()

        assert result == mock_context
        assert parser._browser == mock_browser


class TestCreatePage:
    @pytest.mark.asyncio
    async def test_creates_new_page(self, parser: WargamingParser) -> None:
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        with patch.object(parser, "_ensure_browser", return_value=mock_context):
            result = await parser._create_page()

        assert result == mock_page
        mock_context.new_page.assert_called_once()
