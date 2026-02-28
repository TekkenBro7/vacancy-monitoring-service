from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.comparisons import ComparisonCreate, ComparisonRead, ComparisonUpdate
from src.services.comparison_service import ComparisonService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_async_session)) -> ComparisonService:
    return ComparisonService(db)


@router.get("/users/{user_id}/", response_model=list[ComparisonRead])
async def list_comparisons(
    user_id: int, service: ComparisonService = Depends(get_service)
) -> list[ComparisonRead]:
    return await service.list_comparisons(user_id)


@router.get("/{comp_id}/", response_model=ComparisonRead)
async def get_comparison(
    comp_id: int, service: ComparisonService = Depends(get_service)
) -> ComparisonRead:
    return await service.get_comparison(comp_id)


@router.post("/", response_model=ComparisonRead)
async def create_comparison(
    data: ComparisonCreate, service: ComparisonService = Depends(get_service)
) -> ComparisonRead:
    return await service.create_comparison(data)


@router.patch("/{comp_id}/", response_model=ComparisonRead)
async def update_comparison(
    comp_id: int, data: ComparisonUpdate, service: ComparisonService = Depends(get_service)
) -> ComparisonRead:
    return await service.update_comparison(comp_id, data)


@router.delete("/{comp_id}/")
async def delete_comparison(
    comp_id: int, service: ComparisonService = Depends(get_service)
) -> dict[str, bool | int]:
    return await service.delete_comparison(comp_id)


@router.post("/{comp_id}/vacancies/{vacancy_id}/", response_model=ComparisonRead)
async def add_vacancy(
    comp_id: int, vacancy_id: int, service: ComparisonService = Depends(get_service)
) -> ComparisonRead:
    return await service.add_vacancy(comp_id, vacancy_id)


@router.delete("/{comp_id}/vacancies/{vacancy_id}/", response_model=ComparisonRead)
async def remove_vacancy(
    comp_id: int, vacancy_id: int, service: ComparisonService = Depends(get_service)
) -> ComparisonRead:
    return await service.remove_vacancy(comp_id, vacancy_id)
