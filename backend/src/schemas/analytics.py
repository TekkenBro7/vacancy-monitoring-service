from datetime import date, datetime

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_vacancies: int = 0
    active_vacancies: int = 0
    total_users: int = 0
    total_companies: int = 0
    total_skills: int = 0
    total_sources: int = 0
    total_bookmarks: int = 0
    total_comments: int = 0

    vacancies_with_salary: int = 0
    remote_vacancies: int = 0
    internship_vacancies: int = 0


class StatsChange(BaseModel):
    current: int
    previous: int
    change_percent: float
    trend: str


class OverviewStatsWithTrend(BaseModel):
    vacancies: StatsChange
    users: StatsChange
    companies: StatsChange
    bookmarks: StatsChange


class TimeSeriesPoint(BaseModel):
    date: date
    count: int


class VacanciesTimeSeries(BaseModel):
    period: str
    data: list[TimeSeriesPoint]
    total: int


class DistributionItem(BaseModel):
    id: int | str
    name: str
    count: int
    percentage: float


class SalaryDistributionItem(BaseModel):
    range: str
    range_label: str
    count: int
    percentage: float
    avg_salary: float | None = None


class SalaryStats(BaseModel):
    min_salary: int | None
    max_salary: int | None
    avg_salary: float | None
    median_salary: float | None
    with_salary_count: int
    without_salary_count: int
    distribution: list[SalaryDistributionItem]


class TopCompany(BaseModel):
    id: int
    name: str
    vacancy_count: int
    avg_salary: float | None = None
    has_remote: bool = False


class TopSkill(BaseModel):
    id: int
    name: str
    vacancy_count: int
    percentage: float
    growth: float | None = None


class TopCity(BaseModel):
    id: int
    name: str
    vacancy_count: int
    percentage: float
    avg_salary: float | None = None


class SourceStats(BaseModel):
    id: int
    name: str
    source_type: str
    vacancy_count: int
    active_vacancy_count: int
    percentage: float
    last_parsed: datetime | None = None
    avg_salary: float | None = None


class SourceParsingStats(BaseModel):
    source_id: int
    source_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    pending_tasks: int
    success_rate: float
    last_success: datetime | None = None
    last_failure: datetime | None = None
    avg_parse_duration: float | None = None


class UserActivityStats(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    users_with_bookmarks: int
    users_with_skills: int
    avg_bookmarks_per_user: float
    avg_skills_per_user: float


class UserRegistrationTimeSeries(BaseModel):
    period: str
    data: list[TimeSeriesPoint]
    total_new_users: int


class UsersByRole(BaseModel):
    role_id: int
    role_name: str
    count: int
    percentage: float


class VacancyExperienceStats(BaseModel):
    experience: str
    count: int
    percentage: float
    avg_salary: float | None = None


class VacancyEmploymentStats(BaseModel):
    employment: str
    count: int
    percentage: float


class VacancyScheduleStats(BaseModel):
    schedule: str
    count: int
    percentage: float


class VacancyDetailedStats(BaseModel):
    by_experience: list[VacancyExperienceStats]
    by_employment: list[VacancyEmploymentStats]
    by_schedule: list[VacancyScheduleStats]
    remote_percentage: float
    internship_percentage: float
    with_salary_percentage: float


class FullAnalyticsResponse(BaseModel):
    overview: OverviewStats
    overview_with_trend: OverviewStatsWithTrend | None = None
    vacancies_time_series: VacanciesTimeSeries
    salary_stats: SalaryStats
    top_companies: list[TopCompany]
    top_skills: list[TopSkill]
    top_cities: list[TopCity]
    sources_stats: list[SourceStats]
    vacancy_detailed_stats: VacancyDetailedStats
    user_activity: UserActivityStats
    generated_at: datetime


class DashboardSummary(BaseModel):
    overview: OverviewStats
    top_5_skills: list[TopSkill]
    top_5_companies: list[TopCompany]
    sources_distribution: list[DistributionItem]
    recent_vacancies_count: int
    generated_at: datetime
