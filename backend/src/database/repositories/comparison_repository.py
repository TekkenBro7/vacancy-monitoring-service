from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.database.repositories.base_repository import BaseRepository
from src.models.companies import Vacancy
from src.models.comparisons import Comparison
from src.models.users import User, UserProfile


class ComparisonRepository(BaseRepository[Comparison]):
    async def get_by_user_id(self, user_id: int) -> list[Comparison]:
        stmt = (
            select(Comparison)
            .where(Comparison.user_id == user_id)
            .options(selectinload(Comparison.vacancies))
            .order_by(Comparison.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, comp_id: int) -> Comparison | None:
        stmt = (
            select(Comparison)
            .where(Comparison.id == comp_id)
            .options(selectinload(Comparison.vacancies))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, comp_id: int) -> Comparison | None:
        stmt = (
            select(Comparison)
            .where(Comparison.id == comp_id)
            .options(
                selectinload(Comparison.vacancies).options(
                    selectinload(Vacancy.company),
                    selectinload(Vacancy.skills),
                    selectinload(Vacancy.currency),
                    selectinload(Vacancy.location),
                    selectinload(Vacancy.source),
                ),
                selectinload(Comparison.user).options(
                    selectinload(User.skills),
                    selectinload(User.profile).options(
                        selectinload(UserProfile.city),
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_user(self, name: str, user_id: int) -> Comparison | None:
        stmt = select(Comparison).where(
            Comparison.name == name,
            Comparison.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vacancy_by_id(self, vacancy_id: int) -> Vacancy | None:
        stmt = (
            select(Vacancy)
            .where(Vacancy.id == vacancy_id)
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.skills),
                selectinload(Vacancy.currency),
                selectinload(Vacancy.location),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vacancies_by_ids(self, vacancy_ids: list[int]) -> list[Vacancy]:
        stmt = (
            select(Vacancy)
            .where(Vacancy.id.in_(vacancy_ids))
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.skills),
                selectinload(Vacancy.currency),
                selectinload(Vacancy.location),
                selectinload(Vacancy.source),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_vacancy(self, comp: Comparison, vacancy: Vacancy) -> Comparison:
        if vacancy not in comp.vacancies:
            comp.vacancies.append(vacancy)
            await self.session.commit()
            await self.session.refresh(comp, ["vacancies"])
        return comp

    async def add_vacancies(self, comp: Comparison, vacancies: list[Vacancy]) -> Comparison:
        for vacancy in vacancies:
            if vacancy not in comp.vacancies:
                comp.vacancies.append(vacancy)
        await self.session.commit()
        await self.session.refresh(comp, ["vacancies"])
        return comp

    async def remove_vacancy(self, comp: Comparison, vacancy: Vacancy) -> Comparison:
        if vacancy in comp.vacancies:
            comp.vacancies.remove(vacancy)
            await self.session.commit()
            await self.session.refresh(comp, ["vacancies"])
        return comp

    async def clear_vacancies(self, comp: Comparison) -> Comparison:
        comp.vacancies.clear()
        await self.session.commit()
        await self.session.refresh(comp, ["vacancies"])
        return comp

    async def create_with_refresh(self, comp: Comparison) -> Comparison:
        self.session.add(comp)
        await self.session.commit()
        await self.session.refresh(comp, ["vacancies"])
        return comp

    async def get_user_with_profile(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.skills),
                selectinload(User.profile).options(
                    selectinload(UserProfile.city),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vacancies_by_company(self, company_id: int, limit: int = 10) -> list[Vacancy]:
        stmt = (
            select(Vacancy)
            .where(Vacancy.company_id == company_id)
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.skills),
                selectinload(Vacancy.currency),
                selectinload(Vacancy.location),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_user_comparisons(self, user_id: int) -> int:
        stmt = select(func.count(Comparison.id)).where(Comparison.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
