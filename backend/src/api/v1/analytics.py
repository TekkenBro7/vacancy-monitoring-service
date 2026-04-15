from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.dependencies.users import require_admin
from src.schemas.analytics import (
    DashboardSummary,
    FullAnalyticsResponse,
    OverviewStats,
    OverviewStatsWithTrend,
    SalaryStats,
    SourceParsingStats,
    SourceStats,
    TopCity,
    TopCompany,
    TopSkill,
    UserActivityStats,
    UserRegistrationTimeSeries,
    UsersByRole,
    VacanciesTimeSeries,
    VacancyDetailedStats,
)
from src.schemas.users import UserMe
from src.services.analytics_service import AnalyticsService

router = APIRouter()


def get_analytics_service(db: AsyncSession = Depends(get_async_session)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/overview/", response_model=OverviewStats)
async def get_overview_stats(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> OverviewStats:
    return await service.get_overview_stats()


@router.get("/overview/trends/", response_model=OverviewStatsWithTrend)
async def get_overview_with_trends(
    days: int = Query(30, ge=1, le=365, description="Период для сравнения в днях"),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> OverviewStatsWithTrend:
    return await service.get_overview_with_trend(days)


@router.get("/dashboard/", response_model=FullAnalyticsResponse)
async def get_full_dashboard(
    days: int = Query(30, ge=1, le=365, description="Период в днях"),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> FullAnalyticsResponse:
    return await service.get_full_analytics(days)


@router.get("/dashboard/summary/", response_model=DashboardSummary)
async def get_dashboard_summary(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> DashboardSummary:
    return await service.get_dashboard_summary()


@router.get("/vacancies/time-series/", response_model=VacanciesTimeSeries)
async def get_vacancies_time_series(
    period: str = Query("day", regex="^(day|week|month)$"),
    days: int = Query(30, ge=1, le=365),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> VacanciesTimeSeries:
    return await service.get_vacancies_time_series(period, days)


@router.get("/users/registrations/", response_model=UserRegistrationTimeSeries)
async def get_user_registrations_time_series(
    days: int = Query(30, ge=1, le=365),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> UserRegistrationTimeSeries:
    return await service.get_user_registration_time_series(days)


@router.get("/salary/", response_model=SalaryStats)
async def get_salary_stats(
    currency_id: int | None = Query(None, description="ID валюты для фильтрации"),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> SalaryStats:
    """Статистика по зарплатам"""
    return await service.get_salary_stats(currency_id)


@router.get("/top/companies/", response_model=list[TopCompany])
async def get_top_companies(
    limit: int = Query(10, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[TopCompany]:
    return await service.get_top_companies(limit)


@router.get("/top/skills/", response_model=list[TopSkill])
async def get_top_skills(
    limit: int = Query(20, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[TopSkill]:
    return await service.get_top_skills(limit)


@router.get("/top/cities/", response_model=list[TopCity])
async def get_top_cities(
    limit: int = Query(10, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[TopCity]:
    return await service.get_top_cities(limit)


@router.get("/sources/", response_model=list[SourceStats])
async def get_sources_stats(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[SourceStats]:
    return await service.get_sources_stats()


@router.get("/sources/parsing/", response_model=list[SourceParsingStats])
async def get_source_parsing_stats(
    days: int = Query(7, ge=1, le=30),
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[SourceParsingStats]:
    return await service.get_source_parsing_stats(days)


@router.get("/users/activity/", response_model=UserActivityStats)
async def get_user_activity_stats(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> UserActivityStats:
    return await service.get_user_activity_stats()


@router.get("/users/by-role/", response_model=list[UsersByRole])
async def get_users_by_role(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> list[UsersByRole]:
    return await service.get_users_by_role()


@router.get("/vacancies/detailed/", response_model=VacancyDetailedStats)
async def get_vacancy_detailed_stats(
    service: AnalyticsService = Depends(get_analytics_service),
    _: UserMe = Depends(require_admin),
) -> VacancyDetailedStats:
    return await service.get_vacancy_detailed_stats()
