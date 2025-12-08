from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.company_repository import CompanyRepository
from src.models.companies import Company
from src.schemas.companies import CompanyCreate, CompanyRead, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.repo = CompanyRepository(Company, db)

    async def list_companies(self) -> list[CompanyRead]:
        items = await self.repo.list()
        return [CompanyRead.model_validate(obj) for obj in items]

    async def get_company(self, company_id: int) -> CompanyRead:
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
        return CompanyRead.model_validate(company)

    async def create_company(self, data: CompanyCreate) -> CompanyRead:
        try:
            company_model = Company(
                name=data.name,
                description=data.description,
                website=str(data.website),
            )
            company = await self.repo.create(company_model)
            return CompanyRead.model_validate(company)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Company create conflict",
            ) from e

    async def update_company(self, company_id: int, data: CompanyUpdate) -> CompanyRead:
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            if isinstance(value, HttpUrl):
                value = str(value)
            setattr(company, key, value)

        try:
            updated = await self.repo.update(company)
            return CompanyRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Company update conflict",
            ) from e

    async def delete_company(self, company_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(company_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

        return {"deleted": True, "company_id": company_id}
