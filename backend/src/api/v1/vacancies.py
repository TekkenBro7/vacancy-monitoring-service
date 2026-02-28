from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.companies import VacancyCreate, VacancyRead, VacancyUpdate
from src.services.vacancy_service import VacancyService

router = APIRouter()


def get_vacancy_service(db: AsyncSession = Depends(get_async_session)) -> VacancyService:
    return VacancyService(db)


@router.get("/", response_model=list[VacancyRead])
async def list_vacancies(
    service: VacancyService = Depends(get_vacancy_service),
) -> list[VacancyRead]:
    return await service.list_vacancies()


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
