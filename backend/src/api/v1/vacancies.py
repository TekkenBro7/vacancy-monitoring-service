from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.companies import PaginatedResponse, VacancyCreate, VacancyRead, VacancyUpdate
from src.services.vacancy_service import VacancyService

router = APIRouter()


def get_vacancy_service(db: AsyncSession = Depends(get_async_session)) -> VacancyService:
    return VacancyService(db)


@router.get("/", response_model=PaginatedResponse[VacancyRead])
async def list_vacancies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: VacancyService = Depends(get_vacancy_service),
) -> PaginatedResponse[VacancyRead]:
    return await service.list_vacancies(page=page, page_size=page_size)


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
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancyRead:
    return await service.update_vacancy(vacancy_id, data)


@router.delete("/{vacancy_id}/")
async def delete_vacancy(
    vacancy_id: int,
    service: VacancyService = Depends(get_vacancy_service),
) -> dict[str, bool | int]:
    return await service.delete_vacancy(vacancy_id)
