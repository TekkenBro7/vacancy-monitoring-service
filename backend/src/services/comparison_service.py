from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.groq_client import GroqClient
from src.core.logger import logger
from src.database.repositories.comparison_repository import ComparisonRepository
from src.models.companies import Vacancy
from src.models.comparisons import Comparison
from src.schemas.comparisons import (
    AddVacanciesRequest,
    ComparisonAnalysisRead,
    ComparisonCreate,
    ComparisonDetailRead,
    ComparisonRead,
    ComparisonUpdate,
    VacancyInComparison,
)
from src.services.comparison_analyzer_service import ComparisonAnalyzerService


class ComparisonService:
    MAX_VACANCIES_PER_COMPARISON = 5
    MAX_COMPARISONS_PER_USER = 20

    def __init__(self, db: AsyncSession):
        self.repo = ComparisonRepository(Comparison, db)

    def _vacancy_to_schema(self, vacancy: Vacancy) -> VacancyInComparison:
        return VacancyInComparison(
            id=vacancy.id,
            title=vacancy.title,
            description=vacancy.description,
            salary_from=vacancy.salary_from,
            salary_to=vacancy.salary_to,
            currency_code=vacancy.currency.symbol if vacancy.currency else None,
            company_id=vacancy.company_id,
            company_name=vacancy.company.name if vacancy.company else None,
            city_name=vacancy.location.name if vacancy.location else None,
            address=vacancy.address,
            is_remote=vacancy.is_remote,
            experience=vacancy.experience,
            education=vacancy.education,
            employment=vacancy.employment,
            schedule=vacancy.schedule,
            internship=vacancy.internship,
            skills=[s.name for s in vacancy.skills] if vacancy.skills else [],
            vacancy_url=vacancy.vacancy_url,
            source_name=vacancy.source.name if vacancy.source else None,
            published_at=vacancy.published_at,
        )

    def _to_read_schema(self, comp: Comparison) -> ComparisonRead:
        vacancies = comp.vacancies if comp.vacancies else []
        return ComparisonRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancy_ids=[v.id for v in vacancies],
            vacancies_count=len(vacancies),
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )

    def _to_detail_schema(self, comp: Comparison) -> ComparisonDetailRead:
        vacancies = comp.vacancies if comp.vacancies else []
        return ComparisonDetailRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancies=[self._vacancy_to_schema(v) for v in vacancies],
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )

    async def list_comparisons(self, user_id: int) -> list[ComparisonRead]:
        items = await self.repo.get_by_user_id(user_id)
        return [self._to_read_schema(c) for c in items]

    async def get_comparison(self, comp_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")
        return self._to_read_schema(comp)

    async def get_comparison_detail(self, comp_id: int) -> ComparisonDetailRead:
        comp = await self.repo.get_by_id_with_details(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")
        return self._to_detail_schema(comp)

    async def create_comparison(self, data: ComparisonCreate, user_id: int) -> ComparisonRead:
        count = await self.repo.count_user_comparisons(user_id)
        if count >= self.MAX_COMPARISONS_PER_USER:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Maximum {self.MAX_COMPARISONS_PER_USER} comparisons allowed",
            )

        existing = await self.repo.get_by_name_and_user(data.name, user_id)
        if existing:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Comparison with this name already exists",
            )

        comp = Comparison(name=data.name, user_id=user_id)
        try:
            comp = await self.repo.create_with_refresh(comp)
            return self._to_read_schema(comp)
        except IntegrityError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, "Comparison create conflict") from e

    async def update_comparison(
        self, comp_id: int, data: ComparisonUpdate, user_id: int
    ) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        if data.name is not None:
            existing = await self.repo.get_by_name_and_user(data.name, user_id)
            if existing and existing.id != comp_id:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Comparison with this name already exists",
                )
            comp.name = data.name

        await self.repo.update(comp)

        refreshed = await self.repo.get_by_id(comp_id)
        if not refreshed:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found after update")

        return self._to_read_schema(refreshed)

    async def delete_comparison(self, comp_id: int, user_id: int) -> None:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        await self.repo.delete_by_id(comp_id)

    async def add_vacancy(self, comp_id: int, vacancy_id: int, user_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        if len(comp.vacancies) >= self.MAX_VACANCIES_PER_COMPARISON:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Maximum {self.MAX_VACANCIES_PER_COMPARISON} vacancies per comparison",
            )

        vacancy = await self.repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        comp = await self.repo.add_vacancy(comp, vacancy)
        return self._to_read_schema(comp)

    async def add_vacancies(
        self, comp_id: int, data: AddVacanciesRequest, user_id: int
    ) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        current_ids = {v.id for v in comp.vacancies}
        new_ids = [vid for vid in data.vacancy_ids if vid not in current_ids]

        if len(comp.vacancies) + len(new_ids) > self.MAX_VACANCIES_PER_COMPARISON:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Maximum {self.MAX_VACANCIES_PER_COMPARISON} vacancies per comparison",
            )

        if new_ids:
            vacancies = await self.repo.get_vacancies_by_ids(new_ids)
            if len(vacancies) != len(new_ids):
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Some vacancies not found")
            comp = await self.repo.add_vacancies(comp, vacancies)

        return self._to_read_schema(comp)

    async def remove_vacancy(self, comp_id: int, vacancy_id: int, user_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        vacancy = await self.repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacancy not found")

        comp = await self.repo.remove_vacancy(comp, vacancy)
        return self._to_read_schema(comp)

    async def clear_vacancies(self, comp_id: int, user_id: int) -> ComparisonRead:
        comp = await self.repo.get_by_id(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        comp = await self.repo.clear_vacancies(comp)
        return self._to_read_schema(comp)

    async def analyze_comparison(
        self,
        comp_id: int,
        user_id: int,
        language: str = "ru",
    ) -> ComparisonAnalysisRead:
        comp = await self.repo.get_by_id_with_details(comp_id)
        if not comp:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Comparison not found")

        if comp.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        if len(comp.vacancies) < 2:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "At least 2 vacancies required for analysis",
            )

        user = await self.repo.get_user_with_profile(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        logger.info(f"Starting AI analysis for comparison {comp_id}")

        async with GroqClient() as client:
            analyzer = ComparisonAnalyzerService(client)
            ai_analysis = await analyzer.analyze(
                vacancies=comp.vacancies,
                user=user,
                profile=user.profile,
                language=language,
            )

        return ComparisonAnalysisRead(
            id=comp.id,
            name=comp.name,
            user_id=comp.user_id,
            vacancies=[self._vacancy_to_schema(v) for v in comp.vacancies],
            ai_analysis=ai_analysis,
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )
