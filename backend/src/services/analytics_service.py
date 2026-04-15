from datetime import UTC, date, datetime, timedelta
from statistics import median

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.analytics_repository import AnalyticsRepository
from src.schemas.analytics import (
    DashboardSummary,
    DistributionItem,
    FullAnalyticsResponse,
    OverviewStats,
    OverviewStatsWithTrend,
    SalaryDistributionItem,
    SalaryStats,
    SourceParsingStats,
    SourceStats,
    StatsChange,
    TimeSeriesPoint,
    TopCity,
    TopCompany,
    TopSkill,
    UserActivityStats,
    UserRegistrationTimeSeries,
    UsersByRole,
    VacanciesTimeSeries,
    VacancyDetailedStats,
    VacancyEmploymentStats,
    VacancyExperienceStats,
    VacancyScheduleStats,
)
from src.utils.analytics_utils import normalize_employment, normalize_experience, normalize_schedule


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repo = AnalyticsRepository(db)

    async def get_overview_stats(self) -> OverviewStats:
        vacancy_counts = await self.repo.get_vacancy_counts()
        users_count = await self.repo.count_users()
        companies_count = await self.repo.count_companies()
        skills_count = await self.repo.count_skills()
        sources_count = await self.repo.count_sources()
        bookmarks_count = await self.repo.count_bookmarks()
        comments_count = await self.repo.count_comments()

        return OverviewStats(
            total_vacancies=vacancy_counts["total"],
            active_vacancies=vacancy_counts["active"],
            total_users=users_count,
            total_companies=companies_count,
            total_skills=skills_count,
            total_sources=sources_count,
            total_bookmarks=bookmarks_count,
            total_comments=comments_count,
            vacancies_with_salary=vacancy_counts["with_salary"],
            remote_vacancies=vacancy_counts["remote"],
            internship_vacancies=vacancy_counts["internship"],
        )

    async def get_overview_with_trend(self, days: int = 30) -> OverviewStatsWithTrend:
        now = datetime.now(UTC)
        current_start = now - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)

        current_vacancies = await self.repo.count_vacancies_in_period(current_start, now)
        previous_vacancies = await self.repo.count_vacancies_in_period(
            previous_start, current_start
        )

        current_users = await self.repo.count_users_in_period(current_start, now)
        previous_users = await self.repo.count_users_in_period(previous_start, current_start)

        current_companies = await self.repo.count_companies_in_period(current_start, now)
        previous_companies = await self.repo.count_companies_in_period(
            previous_start, current_start
        )

        current_bookmarks = await self.repo.count_bookmarks_in_period(current_start, now)
        previous_bookmarks = await self.repo.count_bookmarks_in_period(
            previous_start, current_start
        )

        return OverviewStatsWithTrend(
            vacancies=self._calc_change(current_vacancies, previous_vacancies),
            users=self._calc_change(current_users, previous_users),
            companies=self._calc_change(current_companies, previous_companies),
            bookmarks=self._calc_change(current_bookmarks, previous_bookmarks),
        )

    def _calc_change(self, current: int, previous: int) -> StatsChange:
        if previous == 0:
            change_percent = 100.0 if current > 0 else 0.0
        else:
            change_percent = round(((current - previous) / previous) * 100, 1)

        if change_percent > 0:
            trend = "up"
        elif change_percent < 0:
            trend = "down"
        else:
            trend = "stable"

        return StatsChange(
            current=current,
            previous=previous,
            change_percent=change_percent,
            trend=trend,
        )

    async def get_vacancies_time_series(
        self,
        period: str = "day",
        days: int = 30,
    ) -> VacanciesTimeSeries:
        now = datetime.now(UTC)
        start_date = now - timedelta(days=days)

        rows = await self.repo.get_vacancies_by_date(start_date)
        date_counts = {row[0]: row[1] for row in rows}

        data = self._fill_date_gaps(start_date.date(), now.date(), date_counts)

        return VacanciesTimeSeries(
            period=period,
            data=data,
            total=sum(p.count for p in data),
        )

    def _fill_date_gaps(
        self,
        start: date,
        end: date,
        date_counts: dict[date, int],
    ) -> list[TimeSeriesPoint]:
        data = []
        current = start
        while current <= end:
            data.append(TimeSeriesPoint(date=current, count=date_counts.get(current, 0)))
            current += timedelta(days=1)
        return data

    async def get_salary_stats(self, currency_id: int | None = None) -> SalaryStats:
        rows = await self.repo.get_salaries(currency_id)

        salaries: list[float] = []
        for salary_from, salary_to in rows:
            if salary_from and salary_to:
                salaries.append((salary_from + salary_to) / 2)
            elif salary_from:
                salaries.append(float(salary_from))
            elif salary_to:
                salaries.append(float(salary_to))

        with_salary_count = len(salaries)
        without_salary_count = await self.repo.count_vacancies_without_salary()

        min_salary: int | None = None
        max_salary: int | None = None
        avg_salary: float | None = None
        median_salary: float | None = None

        if salaries:
            min_salary = int(min(salaries))
            max_salary = int(max(salaries))
            avg_salary = round(sum(salaries) / len(salaries), 2)
            median_salary = round(median(salaries), 2)

        distribution = self._calc_salary_distribution(salaries, with_salary_count)

        return SalaryStats(
            min_salary=min_salary,
            max_salary=max_salary,
            avg_salary=avg_salary,
            median_salary=median_salary,
            with_salary_count=with_salary_count,
            without_salary_count=without_salary_count,
            distribution=distribution,
        )

    def _calc_salary_distribution(
        self,
        salaries: list[float],
        total: int,
    ) -> list[SalaryDistributionItem]:
        ranges = [
            ("0-50k", "До 50 000", 0, 50000),
            ("50k-100k", "50 000 - 100 000", 50000, 100000),
            ("100k-150k", "100 000 - 150 000", 100000, 150000),
            ("150k-200k", "150 000 - 200 000", 150000, 200000),
            ("200k-300k", "200 000 - 300 000", 200000, 300000),
            ("300k+", "Более 300 000", 300000, float("inf")),
        ]

        distribution = []
        for range_key, range_label, min_val, max_val in ranges:
            range_salaries = [s for s in salaries if min_val <= s < max_val]
            count = len(range_salaries)
            percentage = round((count / total * 100), 1) if total > 0 else 0.0
            avg = round(sum(range_salaries) / len(range_salaries), 2) if range_salaries else None

            distribution.append(
                SalaryDistributionItem(
                    range=range_key,
                    range_label=range_label,
                    count=count,
                    percentage=percentage,
                    avg_salary=avg,
                )
            )

        return distribution

    async def get_top_companies(self, limit: int = 10) -> list[TopCompany]:
        rows = await self.repo.get_top_companies_raw(limit)

        return [
            TopCompany(
                id=row.id,
                name=row.name,
                vacancy_count=row.vacancy_count,
                avg_salary=round(row.avg_salary, 2) if row.avg_salary else None,
                has_remote=row.has_remote or False,
            )
            for row in rows
        ]

    async def get_top_skills(self, limit: int = 20) -> list[TopSkill]:
        total_vacancies = await self.repo.get_active_vacancies_count()
        rows = await self.repo.get_top_skills_raw(limit)

        return [
            TopSkill(
                id=row.id,
                name=row.name,
                vacancy_count=row.vacancy_count,
                percentage=round((row.vacancy_count / total_vacancies) * 100, 1),
                growth=None,
            )
            for row in rows
        ]

    async def get_top_cities(self, limit: int = 10) -> list[TopCity]:
        total_vacancies = await self.repo.get_active_vacancies_count()
        rows = await self.repo.get_top_cities_raw(limit)

        return [
            TopCity(
                id=row.id,
                name=row.name,
                vacancy_count=row.vacancy_count,
                percentage=round((row.vacancy_count / total_vacancies) * 100, 1),
                avg_salary=round(row.avg_salary, 2) if row.avg_salary else None,
            )
            for row in rows
        ]

    async def get_sources_stats(self) -> list[SourceStats]:
        total_vacancies = await self.repo.get_total_vacancies_count()
        rows = await self.repo.get_sources_stats_raw()

        return [
            SourceStats(
                id=row.id,
                name=row.name,
                source_type=row.type_name,
                vacancy_count=row.vacancy_count or 0,
                active_vacancy_count=row.active_count or 0,
                percentage=round((row.vacancy_count or 0) / total_vacancies * 100, 1),
                last_parsed=row.last_parsed,
                avg_salary=round(row.avg_salary, 2) if row.avg_salary else None,
            )
            for row in rows
        ]

    async def get_source_parsing_stats(self, days: int = 7) -> list[SourceParsingStats]:
        start_date = datetime.now(UTC) - timedelta(days=days)
        rows = await self.repo.get_source_parsing_stats_raw(start_date)

        return [
            SourceParsingStats(
                source_id=row.id,
                source_name=row.name,
                total_tasks=row.total or 0,
                successful_tasks=row.success or 0,
                failed_tasks=row.failed or 0,
                pending_tasks=row.pending or 0,
                success_rate=round((row.success or 0) / (row.total or 1) * 100, 1),
                last_success=row.last_success,
                last_failure=row.last_failure,
                avg_parse_duration=round(row.avg_duration, 2) if row.avg_duration else None,
            )
            for row in rows
        ]

    async def get_user_activity_stats(self) -> UserActivityStats:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        total_users = await self.repo.count_users()
        new_today = await self.repo.count_users_since(today_start)
        new_week = await self.repo.count_users_since(week_start)
        new_month = await self.repo.count_users_since(month_start)
        users_with_bookmarks = await self.repo.count_users_with_bookmarks()
        users_with_skills = await self.repo.count_users_with_skills()
        total_bookmarks = await self.repo.count_bookmarks()
        total_user_skills = await self.repo.count_total_user_skills()

        avg_bookmarks = round(total_bookmarks / total_users, 2) if total_users > 0 else 0.0
        avg_skills = round(total_user_skills / total_users, 2) if total_users > 0 else 0.0

        return UserActivityStats(
            total_users=total_users,
            active_users_today=0,
            active_users_week=0,
            active_users_month=0,
            new_users_today=new_today,
            new_users_week=new_week,
            new_users_month=new_month,
            users_with_bookmarks=users_with_bookmarks,
            users_with_skills=users_with_skills,
            avg_bookmarks_per_user=avg_bookmarks,
            avg_skills_per_user=avg_skills,
        )

    async def get_user_registration_time_series(self, days: int = 30) -> UserRegistrationTimeSeries:
        now = datetime.now(UTC)
        start_date = now - timedelta(days=days)

        rows = await self.repo.get_users_by_date(start_date)
        date_counts = {row[0]: row[1] for row in rows}

        data = self._fill_date_gaps(start_date.date(), now.date(), date_counts)

        return UserRegistrationTimeSeries(
            period="day",
            data=data,
            total_new_users=sum(p.count for p in data),
        )

    async def get_users_by_role(self) -> list[UsersByRole]:
        total_users = await self.repo.count_users() or 1
        rows = await self.repo.get_users_by_role_raw()

        return [
            UsersByRole(
                role_id=row.id,
                role_name=row.name,
                count=row.cnt,
                percentage=round((row.cnt / total_users) * 100, 1),
            )
            for row in rows
        ]

    async def get_vacancy_detailed_stats(self) -> VacancyDetailedStats:
        total = await self.repo.get_active_vacancies_count()

        by_experience = await self._get_experience_stats(total)
        by_employment = await self._get_employment_stats(total)
        by_schedule = await self._get_schedule_stats(total)

        remote_count = await self.repo.count_remote_active_vacancies()
        internship_count = await self.repo.count_internship_active_vacancies()
        with_salary_count = await self.repo.count_active_vacancies_with_salary()

        return VacancyDetailedStats(
            by_experience=by_experience,
            by_employment=by_employment,
            by_schedule=by_schedule,
            remote_percentage=round((remote_count / total) * 100, 1),
            internship_percentage=round((internship_count / total) * 100, 1),
            with_salary_percentage=round((with_salary_count / total) * 100, 1),
        )

    async def _get_experience_stats(self, total: int) -> list[VacancyExperienceStats]:
        rows = await self.repo.get_experience_stats_raw()

        experience_groups: dict[str, dict[str, float]] = {}
        for row in rows:
            normalized = normalize_experience(row.experience)
            if normalized not in experience_groups:
                experience_groups[normalized] = {"count": 0, "salary_sum": 0, "salary_count": 0}

            experience_groups[normalized]["count"] += row.cnt
            if row.avg_salary:
                experience_groups[normalized]["salary_sum"] += row.avg_salary * row.cnt
                experience_groups[normalized]["salary_count"] += row.cnt

        experience_order = [
            "Без опыта",
            "1-3 года (Junior)",
            "3-5 лет (Middle)",
            "5+ лет (Senior)",
            "7+ лет (Lead/Expert)",
            "Не указано",
        ]

        result = []
        for exp_name in experience_order:
            if exp_name in experience_groups:
                data = experience_groups[exp_name]
                avg_salary = None
                if data["salary_count"] > 0:
                    avg_salary = round(data["salary_sum"] / data["salary_count"], 2)

                result.append(
                    VacancyExperienceStats(
                        experience=exp_name,
                        count=int(data["count"]),
                        percentage=round((data["count"] / total) * 100, 1),
                        avg_salary=avg_salary,
                    )
                )

        return result

    async def _get_employment_stats(self, total: int) -> list[VacancyEmploymentStats]:
        rows = await self.repo.get_employment_stats_raw()

        employment_groups: dict[str, int] = {}
        for row in rows:
            normalized = normalize_employment(row.employment)
            employment_groups[normalized] = employment_groups.get(normalized, 0) + row.cnt

        return [
            VacancyEmploymentStats(
                employment=emp,
                count=cnt,
                percentage=round((cnt / total) * 100, 1),
            )
            for emp, cnt in sorted(employment_groups.items(), key=lambda x: -x[1])
        ]

    async def _get_schedule_stats(self, total: int) -> list[VacancyScheduleStats]:
        rows = await self.repo.get_schedule_stats_raw()

        schedule_groups: dict[str, int] = {}
        for row in rows:
            normalized = normalize_schedule(row.schedule)
            schedule_groups[normalized] = schedule_groups.get(normalized, 0) + row.cnt

        return [
            VacancyScheduleStats(
                schedule=sch,
                count=cnt,
                percentage=round((cnt / total) * 100, 1),
            )
            for sch, cnt in sorted(schedule_groups.items(), key=lambda x: -x[1])
        ]

    async def get_full_analytics(self, days: int = 30) -> FullAnalyticsResponse:
        overview = await self.get_overview_stats()
        overview_with_trend = await self.get_overview_with_trend(days)
        vacancies_time_series = await self.get_vacancies_time_series(days=days)
        salary_stats = await self.get_salary_stats()
        top_companies = await self.get_top_companies(limit=10)
        top_skills = await self.get_top_skills(limit=20)
        top_cities = await self.get_top_cities(limit=10)
        sources_stats = await self.get_sources_stats()
        vacancy_detailed_stats = await self.get_vacancy_detailed_stats()
        user_activity = await self.get_user_activity_stats()

        return FullAnalyticsResponse(
            overview=overview,
            overview_with_trend=overview_with_trend,
            vacancies_time_series=vacancies_time_series,
            salary_stats=salary_stats,
            top_companies=top_companies,
            top_skills=top_skills,
            top_cities=top_cities,
            sources_stats=sources_stats,
            vacancy_detailed_stats=vacancy_detailed_stats,
            user_activity=user_activity,
            generated_at=datetime.now(UTC),
        )

    async def get_dashboard_summary(self) -> DashboardSummary:
        overview = await self.get_overview_stats()
        top_skills = await self.get_top_skills(limit=5)
        top_companies = await self.get_top_companies(limit=5)

        sources = await self.get_sources_stats()
        sources_distribution = [
            DistributionItem(
                id=s.id,
                name=s.name,
                count=s.vacancy_count,
                percentage=s.percentage,
            )
            for s in sources[:5]
        ]

        yesterday = datetime.now(UTC) - timedelta(days=1)
        recent_count = await self.repo.count_vacancies_since(yesterday)

        return DashboardSummary(
            overview=overview,
            top_5_skills=top_skills,
            top_5_companies=top_companies,
            sources_distribution=sources_distribution,
            recent_vacancies_count=recent_count,
            generated_at=datetime.now(UTC),
        )
