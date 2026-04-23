from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.dependencies.users import get_current_user
from src.models.users import User
from src.schemas.comparisons import (
    AddVacanciesRequest,
    ComparisonAnalysisRead,
    ComparisonCreate,
    ComparisonDetailRead,
    ComparisonRead,
    ComparisonUpdate,
)
from src.services.comparison_service import ComparisonService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> ComparisonService:
    return ComparisonService(db)


@router.get("/", response_model=list[ComparisonRead])
async def list_my_comparisons(
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> list[ComparisonRead]:
    return await service.list_comparisons(current_user.id)


@router.get("/{comp_id}/", response_model=ComparisonRead)
async def get_comparison(
    comp_id: int,
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.get_comparison(comp_id)


@router.get("/{comp_id}/detail/", response_model=ComparisonDetailRead)
async def get_comparison_detail(
    comp_id: int,
    service: ComparisonService = Depends(get_service),
) -> ComparisonDetailRead:
    return await service.get_comparison_detail(comp_id)


@router.post("/", response_model=ComparisonRead, status_code=201)
async def create_comparison(
    data: ComparisonCreate,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.create_comparison(data, current_user.id)


@router.patch("/{comp_id}/", response_model=ComparisonRead)
async def update_comparison(
    comp_id: int,
    data: ComparisonUpdate,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.update_comparison(comp_id, data, current_user.id)


@router.delete("/{comp_id}/", status_code=204)
async def delete_comparison(
    comp_id: int,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> None:
    await service.delete_comparison(comp_id, current_user.id)


@router.post("/{comp_id}/vacancies/{vacancy_id}/", response_model=ComparisonRead)
async def add_vacancy(
    comp_id: int,
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.add_vacancy(comp_id, vacancy_id, current_user.id)


@router.post("/{comp_id}/vacancies/", response_model=ComparisonRead)
async def add_vacancies(
    comp_id: int,
    data: AddVacanciesRequest,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.add_vacancies(comp_id, data, current_user.id)


@router.delete("/{comp_id}/vacancies/{vacancy_id}/", response_model=ComparisonRead)
async def remove_vacancy(
    comp_id: int,
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.remove_vacancy(comp_id, vacancy_id, current_user.id)


@router.delete("/{comp_id}/vacancies/", response_model=ComparisonRead)
async def clear_vacancies(
    comp_id: int,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonRead:
    return await service.clear_vacancies(comp_id, current_user.id)


@router.post("/{comp_id}/analyze/", response_model=ComparisonAnalysisRead)
async def analyze_comparison(
    comp_id: int,
    current_user: User = Depends(get_current_user),
    service: ComparisonService = Depends(get_service),
) -> ComparisonAnalysisRead:
    return await service.analyze_comparison(comp_id, current_user.id)
