from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis_client import redis_client
from src.database.session import get_async_session
from src.dependencies.users import require_admin
from src.schemas.companies import PaginatedResponse, VacancyCreate, VacancyRead, VacancyUpdate
from src.schemas.users import UserMe
from src.schemas.vacancies import (
    AvailableFilters,
    FilterOption,
    SortOrder,
    VacancyFilters,
    VacancySearchResponse,
    VacancySortField,
)
from src.services.vacancy_service import VacancyService

router = APIRouter()


def get_vacancy_service(db: AsyncSession = Depends(get_async_session)) -> VacancyService:
    return VacancyService(db, redis_client=redis_client)


@router.get("/", response_model=PaginatedResponse[VacancyRead])
async def list_vacancies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: VacancyService = Depends(get_vacancy_service),
) -> PaginatedResponse[VacancyRead]:
    return await service.list_vacancies(page=page, page_size=page_size)


@router.get("/search/", response_model=VacancySearchResponse)
async def search_vacancies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Поиск по названию и описанию"),
    source_ids: list[int] | None = Query(None, description="ID источников"),
    company_ids: list[int] | None = Query(None, description="ID компаний"),
    city_ids: list[int] | None = Query(None, description="ID городов"),
    is_remote: bool | None = Query(None, description="Удалённая работа"),
    salary_from: int | None = Query(None, ge=0, description="Зарплата от"),
    salary_to: int | None = Query(None, ge=0, description="Зарплата до"),
    currency_id: int | None = Query(None, description="ID валюты"),
    with_salary_only: bool = Query(False, description="Только с зарплатой"),
    experience: list[str] | None = Query(None, description="Требуемый опыт"),
    employment: list[str] | None = Query(None, description="Тип занятости"),
    schedule: list[str] | None = Query(None, description="График работы"),
    skill_ids: list[int] | None = Query(None, description="ID навыков (все)"),
    internship: bool | None = Query(None, description="Только стажировки"),
    is_active: bool | None = Query(True, description="Только активные"),
    sort_by: VacancySortField = Query(VacancySortField.PUBLISHED_AT),
    sort_order: SortOrder = Query(SortOrder.DESC),
    include_filters: bool = Query(False, description="Включить доступные фильтры"),
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancySearchResponse:
    filters = VacancyFilters(
        search=search,
        source_ids=source_ids,
        company_ids=company_ids,
        city_ids=city_ids,
        is_remote=is_remote,
        salary_from=salary_from,
        salary_to=salary_to,
        currency_id=currency_id,
        with_salary_only=with_salary_only,
        experience=experience,
        employment=employment,
        schedule=schedule,
        skill_ids=skill_ids,
        internship=internship,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return await service.search_vacancies(
        filters=filters,
        page=page,
        page_size=page_size,
        include_filters=include_filters,
    )


@router.get("/filters/", response_model=AvailableFilters)
async def get_available_filters(
    service: VacancyService = Depends(get_vacancy_service),
) -> AvailableFilters:
    result = await service.search_vacancies(
        filters=VacancyFilters(),
        page=1,
        page_size=1,
        include_filters=True,
    )
    if result.filters is None:
        return AvailableFilters()
    return result.filters


@router.get("/filters/search/", response_model=list[FilterOption])
async def search_filter_options(
    filter_type: str = Query(..., description="Тип фильтра: companies, cities, skills"),
    query: str = Query("", description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=200),
    source_ids: list[int] | None = Query(None),
    is_active: bool | None = Query(True),
    service: VacancyService = Depends(get_vacancy_service),
) -> list[FilterOption]:
    return await service.search_filter_options(
        filter_type=filter_type,
        query=query,
        limit=limit,
        base_filters=VacancyFilters(
            source_ids=source_ids,
            is_active=is_active,
        ),
    )


@router.get("/{vacancy_id}/", response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: int, service: VacancyService = Depends(get_vacancy_service)
) -> VacancyRead:
    return await service.get_vacancy(vacancy_id)


@router.post("/", response_model=VacancyRead)
async def create_vacancy(
    data: VacancyCreate,
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancyRead:
    return await service.create_vacancy(data)


@router.patch("/{vacancy_id}/", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: int,
    data: VacancyUpdate,
    db: AsyncSession = Depends(get_async_session),
    service: VacancyService = Depends(get_vacancy_service),
    _: UserMe = Depends(require_admin),
) -> VacancyRead:
    return await service.update_vacancy(vacancy_id, data)


@router.delete("/{vacancy_id}/")
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_async_session),
    service: VacancyService = Depends(get_vacancy_service),
    _: UserMe = Depends(require_admin),
) -> dict[str, bool | int]:
    return await service.delete_vacancy(vacancy_id)
