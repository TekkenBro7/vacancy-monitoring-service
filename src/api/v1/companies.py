from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.companies import CompanyCreate, CompanyRead, CompanyUpdate
from src.services.company_service import CompanyService

router = APIRouter()


def get_company_service(db: AsyncSession = Depends(get_async_session)) -> CompanyService:
    return CompanyService(db)


@router.get("/", response_model=list[CompanyRead])
async def list_companies(
    service: CompanyService = Depends(get_company_service),
) -> list[CompanyRead]:
    return await service.list_companies()


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int, service: CompanyService = Depends(get_company_service)
) -> CompanyRead:
    return await service.get_company(company_id)


@router.post("/", response_model=CompanyRead)
async def create_company(
    data: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
) -> CompanyRead:
    return await service.create_company(data)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service),
) -> CompanyRead:
    return await service.update_company(company_id, data)


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    service: CompanyService = Depends(get_company_service),
) -> dict[str, bool | int]:
    return await service.delete_company(company_id)
