from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.analytics_service import AnalyticsService


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> AnalyticsService:
    svc = AnalyticsService.__new__(AnalyticsService)
    svc.repo = mock_repo
    return svc


class TestCalcChange:
    @pytest.fixture
    def service_instance(self) -> AnalyticsService:
        return AnalyticsService.__new__(AnalyticsService)

    def test_trend_up_when_current_greater(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=150, previous=100)

        assert result.current == 150
        assert result.previous == 100
        assert result.change_percent == 50.0
        assert result.trend == "up"

    def test_trend_down_when_current_less(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=50, previous=100)

        assert result.current == 50
        assert result.previous == 100
        assert result.change_percent == -50.0
        assert result.trend == "down"

    def test_trend_stable_when_equal(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=100, previous=100)

        assert result.change_percent == 0.0
        assert result.trend == "stable"

    def test_handles_zero_previous_with_positive_current(
        self, service_instance: AnalyticsService
    ) -> None:
        result = service_instance._calc_change(current=100, previous=0)

        assert result.change_percent == 100.0
        assert result.trend == "up"

    def test_handles_both_zero(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=0, previous=0)

        assert result.change_percent == 0.0
        assert result.trend == "stable"

    def test_rounds_to_one_decimal(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=133, previous=100)

        assert result.change_percent == 33.0

    def test_negative_percentage_rounded(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_change(current=67, previous=100)

        assert result.change_percent == -33.0


class TestFillDateGaps:
    @pytest.fixture
    def service_instance(self) -> AnalyticsService:
        return AnalyticsService.__new__(AnalyticsService)

    def test_fills_missing_dates_with_zeros(self, service_instance: AnalyticsService) -> None:
        start = date(2024, 1, 1)
        end = date(2024, 1, 5)
        date_counts = {
            date(2024, 1, 1): 10,
            date(2024, 1, 3): 5,
            date(2024, 1, 5): 15,
        }

        result = service_instance._fill_date_gaps(start, end, date_counts)

        assert len(result) == 5
        assert result[0].date == date(2024, 1, 1)
        assert result[0].count == 10
        assert result[1].date == date(2024, 1, 2)
        assert result[1].count == 0
        assert result[2].date == date(2024, 1, 3)
        assert result[2].count == 5
        assert result[3].date == date(2024, 1, 4)
        assert result[3].count == 0
        assert result[4].date == date(2024, 1, 5)
        assert result[4].count == 15

    def test_single_day_range(self, service_instance: AnalyticsService) -> None:
        start = date(2024, 1, 1)
        end = date(2024, 1, 1)
        date_counts = {date(2024, 1, 1): 42}

        result = service_instance._fill_date_gaps(start, end, date_counts)

        assert len(result) == 1
        assert result[0].count == 42

    def test_empty_date_counts(self, service_instance: AnalyticsService) -> None:
        start = date(2024, 1, 1)
        end = date(2024, 1, 3)

        result = service_instance._fill_date_gaps(start, end, {})

        assert len(result) == 3
        assert all(p.count == 0 for p in result)


class TestCalcSalaryDistribution:
    @pytest.fixture
    def service_instance(self) -> AnalyticsService:
        return AnalyticsService.__new__(AnalyticsService)

    def test_distributes_salaries_correctly(self, service_instance: AnalyticsService) -> None:
        salaries = [
            30000.0,
            75000.0,
            125000.0,
            175000.0,
            250000.0,
            400000.0,
        ]

        result = service_instance._calc_salary_distribution(salaries, total=6)

        assert len(result) == 6
        assert result[0].range == "0-50k"
        assert result[0].count == 1
        assert result[0].percentage == pytest.approx(16.7, rel=0.1)
        assert result[0].avg_salary == 30000.0

    def test_handles_empty_salaries(self, service_instance: AnalyticsService) -> None:
        result = service_instance._calc_salary_distribution([], total=0)

        assert len(result) == 6
        for item in result:
            assert item.count == 0
            assert item.percentage == 0.0
            assert item.avg_salary is None

    def test_multiple_salaries_in_same_range(self, service_instance: AnalyticsService) -> None:
        salaries = [60000.0, 70000.0, 80000.0, 90000.0]
        result = service_instance._calc_salary_distribution(salaries, total=4)

        assert result[1].range == "50k-100k"
        assert result[1].count == 4
        assert result[1].percentage == 100.0
        assert result[1].avg_salary == 75000.0

    def test_high_salaries_300k_plus(self, service_instance: AnalyticsService) -> None:
        salaries = [350000.0, 500000.0, 1000000.0]

        result = service_instance._calc_salary_distribution(salaries, total=3)

        assert result[5].range == "300k+"
        assert result[5].count == 3
        assert result[5].percentage == 100.0


class TestGetOverviewStats:
    @pytest.mark.asyncio
    async def test_returns_overview_stats(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 100,
            "active": 80,
            "with_salary": 60,
            "remote": 40,
            "internship": 10,
        }
        mock_repo.count_users.return_value = 50
        mock_repo.count_companies.return_value = 30
        mock_repo.count_skills.return_value = 200
        mock_repo.count_sources.return_value = 5
        mock_repo.count_bookmarks.return_value = 150
        mock_repo.count_comments.return_value = 25

        result = await service.get_overview_stats()

        assert result.total_vacancies == 100
        assert result.active_vacancies == 80
        assert result.total_users == 50
        assert result.total_companies == 30
        assert result.total_skills == 200
        assert result.total_sources == 5
        assert result.total_bookmarks == 150
        assert result.total_comments == 25
        assert result.vacancies_with_salary == 60
        assert result.remote_vacancies == 40
        assert result.internship_vacancies == 10

    @pytest.mark.asyncio
    async def test_calls_all_repo_methods(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 0,
            "active": 0,
            "with_salary": 0,
            "remote": 0,
            "internship": 0,
        }
        mock_repo.count_users.return_value = 0
        mock_repo.count_companies.return_value = 0
        mock_repo.count_skills.return_value = 0
        mock_repo.count_sources.return_value = 0
        mock_repo.count_bookmarks.return_value = 0
        mock_repo.count_comments.return_value = 0

        await service.get_overview_stats()

        mock_repo.get_vacancy_counts.assert_called_once()
        mock_repo.count_users.assert_called_once()
        mock_repo.count_companies.assert_called_once()
        mock_repo.count_skills.assert_called_once()
        mock_repo.count_sources.assert_called_once()
        mock_repo.count_bookmarks.assert_called_once()
        mock_repo.count_comments.assert_called_once()


class TestGetOverviewWithTrend:
    @pytest.mark.asyncio
    async def test_calculates_trends_correctly(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_vacancies_in_period.side_effect = [100, 80]
        mock_repo.count_users_in_period.side_effect = [50, 50]
        mock_repo.count_companies_in_period.side_effect = [30, 40]
        mock_repo.count_bookmarks_in_period.side_effect = [200, 0]

        result = await service.get_overview_with_trend(days=30)

        assert result.vacancies.trend == "up"
        assert result.vacancies.current == 100
        assert result.vacancies.previous == 80
        assert result.users.trend == "stable"
        assert result.companies.trend == "down"
        assert result.bookmarks.trend == "up"
        assert result.bookmarks.change_percent == 100.0

    @pytest.mark.asyncio
    async def test_uses_correct_periods(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_vacancies_in_period.return_value = 0
        mock_repo.count_users_in_period.return_value = 0
        mock_repo.count_companies_in_period.return_value = 0
        mock_repo.count_bookmarks_in_period.return_value = 0

        await service.get_overview_with_trend(days=7)

        assert mock_repo.count_vacancies_in_period.call_count == 2
        assert mock_repo.count_users_in_period.call_count == 2


class TestGetVacanciesTimeSeries:
    @pytest.mark.asyncio
    async def test_returns_time_series(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        today = datetime.now(UTC).date()
        mock_repo.get_vacancies_by_date.return_value = [
            (today, 10),
            (today - timedelta(days=1), 5),
        ]

        result = await service.get_vacancies_time_series(period="day", days=3)

        assert result.period == "day"
        assert len(result.data) == 4
        assert result.total == 15

    @pytest.mark.asyncio
    async def test_fills_gaps_with_zeros(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        today = datetime.now(UTC).date()
        mock_repo.get_vacancies_by_date.return_value = [(today, 10)]

        result = await service.get_vacancies_time_series(days=5)

        assert len(result.data) == 6
        zero_days = [p for p in result.data if p.count == 0]
        assert len(zero_days) == 5

    @pytest.mark.asyncio
    async def test_empty_data(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_vacancies_by_date.return_value = []

        result = await service.get_vacancies_time_series(days=7)

        assert result.total == 0
        assert len(result.data) == 8


class TestGetSalaryStats:
    @pytest.mark.asyncio
    async def test_calculates_salary_statistics(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_salaries.return_value = [
            (100000, 150000),
            (80000, 120000),
            (200000, None),
            (None, 60000),
        ]
        mock_repo.count_vacancies_without_salary.return_value = 10

        result = await service.get_salary_stats()

        assert result.min_salary == 60000
        assert result.max_salary == 200000
        assert result.with_salary_count == 4
        assert result.without_salary_count == 10
        assert result.avg_salary is not None
        assert result.median_salary is not None

    @pytest.mark.asyncio
    async def test_handles_empty_salaries(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_salaries.return_value = []
        mock_repo.count_vacancies_without_salary.return_value = 50

        result = await service.get_salary_stats()

        assert result.min_salary is None
        assert result.max_salary is None
        assert result.avg_salary is None
        assert result.median_salary is None
        assert result.with_salary_count == 0
        assert result.without_salary_count == 50

    @pytest.mark.asyncio
    async def test_passes_currency_filter(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_salaries.return_value = []
        mock_repo.count_vacancies_without_salary.return_value = 0

        await service.get_salary_stats(currency_id=5)

        mock_repo.get_salaries.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_only_salary_from(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_salaries.return_value = [(100000, None)]
        mock_repo.count_vacancies_without_salary.return_value = 0

        result = await service.get_salary_stats()

        assert result.min_salary == 100000
        assert result.max_salary == 100000

    @pytest.mark.asyncio
    async def test_only_salary_to(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_salaries.return_value = [(None, 80000)]
        mock_repo.count_vacancies_without_salary.return_value = 0

        result = await service.get_salary_stats()

        assert result.min_salary == 80000
        assert result.max_salary == 80000

    @pytest.mark.asyncio
    async def test_distribution_included(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_salaries.return_value = [(100000, 150000)]
        mock_repo.count_vacancies_without_salary.return_value = 0

        result = await service.get_salary_stats()

        assert len(result.distribution) == 6
        assert result.distribution[2].range == "100k-150k"
        assert result.distribution[2].count == 1


class TestGetTopCompanies:
    @pytest.mark.asyncio
    async def test_returns_companies(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_company = MagicMock()
        mock_company.id = 1
        mock_company.name = "Test Company"
        mock_company.vacancy_count = 50
        mock_company.avg_salary = 150000.0
        mock_company.has_remote = True

        mock_repo.get_top_companies_raw.return_value = [mock_company]

        result = await service.get_top_companies(limit=10)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Test Company"
        assert result[0].vacancy_count == 50
        assert result[0].avg_salary == 150000.0
        assert result[0].has_remote is True

    @pytest.mark.asyncio
    async def test_rounds_avg_salary(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_company = MagicMock()
        mock_company.id = 1
        mock_company.name = "Test"
        mock_company.vacancy_count = 10
        mock_company.avg_salary = 150000.126
        mock_company.has_remote = False

        mock_repo.get_top_companies_raw.return_value = [mock_company]

        result = await service.get_top_companies()

        assert result[0].avg_salary == 150000.13

    @pytest.mark.asyncio
    async def test_handles_null_avg_salary(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_company = MagicMock()
        mock_company.id = 1
        mock_company.name = "No Salary Company"
        mock_company.vacancy_count = 10
        mock_company.avg_salary = None
        mock_company.has_remote = False

        mock_repo.get_top_companies_raw.return_value = [mock_company]

        result = await service.get_top_companies()

        assert result[0].avg_salary is None
        assert result[0].has_remote is False

    @pytest.mark.asyncio
    async def test_passes_limit(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_top_companies_raw.return_value = []

        await service.get_top_companies(limit=5)

        mock_repo.get_top_companies_raw.assert_called_once_with(5)


class TestGetTopSkills:
    @pytest.mark.asyncio
    async def test_returns_skills_with_percentage(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_active_vacancies_count.return_value = 100

        mock_skill = MagicMock()
        mock_skill.id = 1
        mock_skill.name = "Python"
        mock_skill.vacancy_count = 50

        mock_repo.get_top_skills_raw.return_value = [mock_skill]

        result = await service.get_top_skills(limit=10)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Python"
        assert result[0].vacancy_count == 50
        assert result[0].percentage == 50.0
        assert result[0].growth is None

    @pytest.mark.asyncio
    async def test_passes_limit(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_active_vacancies_count.return_value = 100
        mock_repo.get_top_skills_raw.return_value = []

        await service.get_top_skills(limit=15)

        mock_repo.get_top_skills_raw.assert_called_once_with(15)


class TestGetTopCities:
    @pytest.mark.asyncio
    async def test_returns_cities_with_percentage(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_active_vacancies_count.return_value = 200

        mock_city = MagicMock()
        mock_city.id = 1
        mock_city.name = "Moscow"
        mock_city.vacancy_count = 100
        mock_city.avg_salary = 180000.0

        mock_repo.get_top_cities_raw.return_value = [mock_city]

        result = await service.get_top_cities(limit=10)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Moscow"
        assert result[0].vacancy_count == 100
        assert result[0].percentage == 50.0
        assert result[0].avg_salary == 180000.0

    @pytest.mark.asyncio
    async def test_rounds_avg_salary(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_active_vacancies_count.return_value = 100

        mock_city = MagicMock()
        mock_city.id = 1
        mock_city.name = "Moscow"
        mock_city.vacancy_count = 50
        mock_city.avg_salary = 180000.456

        mock_repo.get_top_cities_raw.return_value = [mock_city]

        result = await service.get_top_cities()

        assert result[0].avg_salary == 180000.46

    @pytest.mark.asyncio
    async def test_handles_null_avg_salary(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_active_vacancies_count.return_value = 100

        mock_city = MagicMock()
        mock_city.id = 1
        mock_city.name = "Unknown"
        mock_city.vacancy_count = 10
        mock_city.avg_salary = None

        mock_repo.get_top_cities_raw.return_value = [mock_city]

        result = await service.get_top_cities()

        assert result[0].avg_salary is None


class TestGetSourcesStats:
    @pytest.mark.asyncio
    async def test_returns_sources_stats(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_total_vacancies_count.return_value = 100

        mock_source = MagicMock()
        mock_source.id = 1
        mock_source.name = "HeadHunter"
        mock_source.type_name = "API"
        mock_source.vacancy_count = 80
        mock_source.active_count = 60
        mock_source.last_parsed = datetime.now(UTC)
        mock_source.avg_salary = 150000.0

        mock_repo.get_sources_stats_raw.return_value = [mock_source]

        result = await service.get_sources_stats()

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "HeadHunter"
        assert result[0].source_type == "API"
        assert result[0].vacancy_count == 80
        assert result[0].active_vacancy_count == 60
        assert result[0].percentage == 80.0

    @pytest.mark.asyncio
    async def test_handles_null_values(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_total_vacancies_count.return_value = 100

        mock_source = MagicMock()
        mock_source.id = 1
        mock_source.name = "Test"
        mock_source.type_name = "Parser"
        mock_source.vacancy_count = None
        mock_source.active_count = None
        mock_source.last_parsed = None
        mock_source.avg_salary = None

        mock_repo.get_sources_stats_raw.return_value = [mock_source]

        result = await service.get_sources_stats()

        assert result[0].vacancy_count == 0
        assert result[0].active_vacancy_count == 0
        assert result[0].avg_salary is None


class TestGetSourceParsingStats:
    @pytest.mark.asyncio
    async def test_returns_parsing_stats(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_stat = MagicMock()
        mock_stat.id = 1
        mock_stat.name = "HeadHunter"
        mock_stat.total = 100
        mock_stat.success = 95
        mock_stat.failed = 3
        mock_stat.pending = 2
        mock_stat.last_success = datetime.now(UTC)
        mock_stat.last_failure = datetime.now(UTC) - timedelta(days=1)
        mock_stat.avg_duration = 5.5

        mock_repo.get_source_parsing_stats_raw.return_value = [mock_stat]

        result = await service.get_source_parsing_stats(days=7)

        assert len(result) == 1
        assert result[0].source_id == 1
        assert result[0].source_name == "HeadHunter"
        assert result[0].total_tasks == 100
        assert result[0].successful_tasks == 95
        assert result[0].failed_tasks == 3
        assert result[0].pending_tasks == 2
        assert result[0].success_rate == 95.0
        assert result[0].avg_parse_duration == 5.5

    @pytest.mark.asyncio
    async def test_rounds_avg_duration(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_stat = MagicMock()
        mock_stat.id = 1
        mock_stat.name = "Test"
        mock_stat.total = 10
        mock_stat.success = 8
        mock_stat.failed = 2
        mock_stat.pending = 0
        mock_stat.last_success = None
        mock_stat.last_failure = None
        mock_stat.avg_duration = 3.456

        mock_repo.get_source_parsing_stats_raw.return_value = [mock_stat]

        result = await service.get_source_parsing_stats()

        assert result[0].avg_parse_duration == 3.46

    @pytest.mark.asyncio
    async def test_handles_null_values(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_stat = MagicMock()
        mock_stat.id = 1
        mock_stat.name = "Test"
        mock_stat.total = None
        mock_stat.success = None
        mock_stat.failed = None
        mock_stat.pending = None
        mock_stat.last_success = None
        mock_stat.last_failure = None
        mock_stat.avg_duration = None

        mock_repo.get_source_parsing_stats_raw.return_value = [mock_stat]

        result = await service.get_source_parsing_stats()

        assert result[0].total_tasks == 0
        assert result[0].successful_tasks == 0
        assert result[0].success_rate == 0.0
        assert result[0].avg_parse_duration is None


class TestGetUserActivityStats:
    @pytest.mark.asyncio
    async def test_calculates_user_stats(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_users.return_value = 100
        mock_repo.count_users_since.side_effect = [5, 20, 50]
        mock_repo.count_users_with_bookmarks.return_value = 30
        mock_repo.count_users_with_skills.return_value = 50
        mock_repo.count_bookmarks.return_value = 300
        mock_repo.count_total_user_skills.return_value = 400

        result = await service.get_user_activity_stats()

        assert result.total_users == 100
        assert result.new_users_today == 5
        assert result.new_users_week == 20
        assert result.new_users_month == 50
        assert result.users_with_bookmarks == 30
        assert result.users_with_skills == 50
        assert result.avg_bookmarks_per_user == 3.0
        assert result.avg_skills_per_user == 4.0

    @pytest.mark.asyncio
    async def test_handles_zero_users(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_users.return_value = 0
        mock_repo.count_users_since.return_value = 0
        mock_repo.count_users_with_bookmarks.return_value = 0
        mock_repo.count_users_with_skills.return_value = 0
        mock_repo.count_bookmarks.return_value = 0
        mock_repo.count_total_user_skills.return_value = 0

        result = await service.get_user_activity_stats()

        assert result.avg_bookmarks_per_user == 0.0
        assert result.avg_skills_per_user == 0.0


class TestGetUserRegistrationTimeSeries:
    @pytest.mark.asyncio
    async def test_returns_time_series(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        today = datetime.now(UTC).date()
        mock_repo.get_users_by_date.return_value = [
            (today, 5),
            (today - timedelta(days=1), 3),
        ]

        result = await service.get_user_registration_time_series(days=7)

        assert result.period == "day"
        assert result.total_new_users == 8
        assert len(result.data) == 8

    @pytest.mark.asyncio
    async def test_empty_registrations(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_users_by_date.return_value = []

        result = await service.get_user_registration_time_series(days=5)

        assert result.total_new_users == 0
        assert len(result.data) == 6


class TestGetUsersByRole:
    @pytest.mark.asyncio
    async def test_returns_users_by_role(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_users.return_value = 100

        mock_role = MagicMock()
        mock_role.id = 1
        mock_role.name = "user"
        mock_role.cnt = 80

        mock_repo.get_users_by_role_raw.return_value = [mock_role]

        result = await service.get_users_by_role()

        assert len(result) == 1
        assert result[0].role_id == 1
        assert result[0].role_name == "user"
        assert result[0].count == 80
        assert result[0].percentage == 80.0

    @pytest.mark.asyncio
    async def test_handles_zero_users(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.count_users.return_value = 0
        mock_repo.get_users_by_role_raw.return_value = []

        result = await service.get_users_by_role()

        assert len(result) == 0


class TestGetVacancyDetailedStats:
    @pytest.mark.asyncio
    async def test_calculates_percentages(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_active_vacancies_count.return_value = 100
        mock_repo.get_experience_stats_raw.return_value = []
        mock_repo.get_employment_stats_raw.return_value = []
        mock_repo.get_schedule_stats_raw.return_value = []
        mock_repo.count_remote_active_vacancies.return_value = 40
        mock_repo.count_internship_active_vacancies.return_value = 10
        mock_repo.count_active_vacancies_with_salary.return_value = 70

        result = await service.get_vacancy_detailed_stats()

        assert result.remote_percentage == 40.0
        assert result.internship_percentage == 10.0
        assert result.with_salary_percentage == 70.0
        assert result.by_experience == []
        assert result.by_employment == []
        assert result.by_schedule == []


class TestGetExperienceStats:
    @pytest.mark.asyncio
    async def test_groups_and_normalizes_experience(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_exp1 = MagicMock()
        mock_exp1.experience = "От 1 года до 3 лет"
        mock_exp1.cnt = 50
        mock_exp1.avg_salary = 100000.0

        mock_exp2 = MagicMock()
        mock_exp2.experience = "между 1 и 3 годами"
        mock_exp2.cnt = 30
        mock_exp2.avg_salary = 120000.0

        mock_repo.get_experience_stats_raw.return_value = [mock_exp1, mock_exp2]

        result = await service._get_experience_stats(total=100)

        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_empty_experience(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_experience_stats_raw.return_value = []

        result = await service._get_experience_stats(total=100)

        assert result == []


class TestGetEmploymentStats:
    @pytest.mark.asyncio
    async def test_groups_employment(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_emp = MagicMock()
        mock_emp.employment = "Полная занятость"
        mock_emp.cnt = 80

        mock_repo.get_employment_stats_raw.return_value = [mock_emp]

        result = await service._get_employment_stats(total=100)

        assert len(result) >= 1
        assert result[0].count == 80

    @pytest.mark.asyncio
    async def test_sorted_by_count_desc(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_emp1 = MagicMock()
        mock_emp1.employment = "Частичная занятость"
        mock_emp1.cnt = 20

        mock_emp2 = MagicMock()
        mock_emp2.employment = "Полная занятость"
        mock_emp2.cnt = 80

        mock_repo.get_employment_stats_raw.return_value = [mock_emp1, mock_emp2]

        result = await service._get_employment_stats(total=100)

        assert result[0].count >= result[-1].count


class TestGetScheduleStats:
    @pytest.mark.asyncio
    async def test_groups_schedule(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_sch = MagicMock()
        mock_sch.schedule = "Удаленная работа"
        mock_sch.cnt = 50

        mock_repo.get_schedule_stats_raw.return_value = [mock_sch]

        result = await service._get_schedule_stats(total=100)

        assert len(result) >= 1
        assert result[0].percentage == 50.0


class TestGetFullAnalytics:
    @pytest.mark.asyncio
    async def test_returns_full_response(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 100,
            "active": 80,
            "with_salary": 60,
            "remote": 40,
            "internship": 10,
        }
        mock_repo.count_users.return_value = 50
        mock_repo.count_companies.return_value = 30
        mock_repo.count_skills.return_value = 200
        mock_repo.count_sources.return_value = 5
        mock_repo.count_bookmarks.return_value = 150
        mock_repo.count_comments.return_value = 25
        mock_repo.count_vacancies_in_period.return_value = 50
        mock_repo.count_users_in_period.return_value = 10
        mock_repo.count_companies_in_period.return_value = 5
        mock_repo.count_bookmarks_in_period.return_value = 30
        mock_repo.get_vacancies_by_date.return_value = []
        mock_repo.get_salaries.return_value = []
        mock_repo.count_vacancies_without_salary.return_value = 0
        mock_repo.get_top_companies_raw.return_value = []
        mock_repo.get_active_vacancies_count.return_value = 80
        mock_repo.get_top_skills_raw.return_value = []
        mock_repo.get_top_cities_raw.return_value = []
        mock_repo.get_total_vacancies_count.return_value = 100
        mock_repo.get_sources_stats_raw.return_value = []
        mock_repo.get_experience_stats_raw.return_value = []
        mock_repo.get_employment_stats_raw.return_value = []
        mock_repo.get_schedule_stats_raw.return_value = []
        mock_repo.count_remote_active_vacancies.return_value = 40
        mock_repo.count_internship_active_vacancies.return_value = 10
        mock_repo.count_active_vacancies_with_salary.return_value = 60
        mock_repo.count_users_since.return_value = 5
        mock_repo.count_users_with_bookmarks.return_value = 20
        mock_repo.count_users_with_skills.return_value = 30
        mock_repo.count_total_user_skills.return_value = 100

        result = await service.get_full_analytics(days=30)

        assert result.overview is not None
        assert result.overview_with_trend is not None
        assert result.vacancies_time_series is not None
        assert result.salary_stats is not None
        assert result.top_companies is not None
        assert result.top_skills is not None
        assert result.top_cities is not None
        assert result.sources_stats is not None
        assert result.vacancy_detailed_stats is not None
        assert result.user_activity is not None
        assert result.generated_at is not None


class TestGetDashboardSummary:
    @pytest.mark.asyncio
    async def test_returns_dashboard_summary(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 100,
            "active": 80,
            "with_salary": 60,
            "remote": 40,
            "internship": 10,
        }
        mock_repo.count_users.return_value = 50
        mock_repo.count_companies.return_value = 30
        mock_repo.count_skills.return_value = 200
        mock_repo.count_sources.return_value = 5
        mock_repo.count_bookmarks.return_value = 150
        mock_repo.count_comments.return_value = 25
        mock_repo.get_active_vacancies_count.return_value = 80
        mock_repo.get_top_skills_raw.return_value = []
        mock_repo.get_top_companies_raw.return_value = []
        mock_repo.get_total_vacancies_count.return_value = 100
        mock_repo.get_sources_stats_raw.return_value = []
        mock_repo.count_vacancies_since.return_value = 15

        result = await service.get_dashboard_summary()

        assert result.overview is not None
        assert result.top_5_skills is not None
        assert result.top_5_companies is not None
        assert result.sources_distribution is not None
        assert result.recent_vacancies_count == 15
        assert result.generated_at is not None

    @pytest.mark.asyncio
    async def test_limits_to_5_items(self, service: AnalyticsService, mock_repo: AsyncMock) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 100,
            "active": 80,
            "with_salary": 60,
            "remote": 40,
            "internship": 10,
        }
        mock_repo.count_users.return_value = 50
        mock_repo.count_companies.return_value = 30
        mock_repo.count_skills.return_value = 200
        mock_repo.count_sources.return_value = 5
        mock_repo.count_bookmarks.return_value = 150
        mock_repo.count_comments.return_value = 25
        mock_repo.get_active_vacancies_count.return_value = 80
        mock_repo.get_top_skills_raw.return_value = []
        mock_repo.get_top_companies_raw.return_value = []
        mock_repo.get_total_vacancies_count.return_value = 100
        mock_repo.get_sources_stats_raw.return_value = []
        mock_repo.count_vacancies_since.return_value = 0

        await service.get_dashboard_summary()

        mock_repo.get_top_skills_raw.assert_called_with(5)
        mock_repo.get_top_companies_raw.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_sources_distribution_limited(
        self, service: AnalyticsService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_vacancy_counts.return_value = {
            "total": 100,
            "active": 80,
            "with_salary": 60,
            "remote": 40,
            "internship": 10,
        }
        mock_repo.count_users.return_value = 50
        mock_repo.count_companies.return_value = 30
        mock_repo.count_skills.return_value = 200
        mock_repo.count_sources.return_value = 10
        mock_repo.count_bookmarks.return_value = 150
        mock_repo.count_comments.return_value = 25
        mock_repo.get_active_vacancies_count.return_value = 80
        mock_repo.get_top_skills_raw.return_value = []
        mock_repo.get_top_companies_raw.return_value = []
        mock_repo.get_total_vacancies_count.return_value = 100

        mock_sources = []
        for i in range(10):
            mock_source = MagicMock()
            mock_source.id = i
            mock_source.name = f"Source {i}"
            mock_source.type_name = "API"
            mock_source.vacancy_count = 10 - i
            mock_source.active_count = 5
            mock_source.last_parsed = None
            mock_source.avg_salary = None
            mock_sources.append(mock_source)

        mock_repo.get_sources_stats_raw.return_value = mock_sources
        mock_repo.count_vacancies_since.return_value = 0

        result = await service.get_dashboard_summary()

        assert len(result.sources_distribution) == 5
