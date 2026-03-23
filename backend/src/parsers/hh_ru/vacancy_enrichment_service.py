from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import HHConfig
from src.core.logger import logger
from src.database.repositories.skill_repository import SkillRepository
from src.models.companies import Vacancy
from src.models.skills import Skill
from src.parsers.hh_ru.hh_parser import HHParser


class VacancyEnrichmentService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.skill_repository = SkillRepository(Skill, self.db)
        self.parser = HHParser()

    async def enrich_vacancy_if_needed(self, vacancy: Vacancy) -> Vacancy:
        should_enrich, reason = self._should_enrich(vacancy)

        if not should_enrich:
            logger.info(f"Vacancy {vacancy.id} does not need enrichment: {reason}")
            return vacancy

        logger.info(
            f"Enriching vacancy {vacancy.id} from HH.ru API (external_id: {vacancy.external_id}). Reason: {reason}"
        )

        enriched_data = await self.enrich_vacancy_data(vacancy.external_id)

        if enriched_data:
            logger.info(
                f"Successfully enriched vacancy {vacancy.id} with {len(enriched_data.get('skills', []))} skills"
            )
            await self._update_vacancy(vacancy, enriched_data)
            vacancy.last_enriched_at = datetime.now(UTC)
        else:
            logger.warning(
                f"Failed to enrich vacancy {vacancy.id} from HH.ru API - no data returned"
            )

        return vacancy

    def _should_enrich(self, vacancy: Vacancy) -> tuple[bool, str]:
        if not vacancy.source:
            return False, "No source"

        if vacancy.source.name != HHConfig.HH_SOURCE_NAME:
            return False, f"Source is {vacancy.source.name}, not HeadHunter"

        if not vacancy.external_id:
            return False, "No external_id"

        description = vacancy.description or ""
        has_description = len(description.strip()) > 0
        has_skills = bool(vacancy.skills and len(vacancy.skills) > 0)

        if not has_description:
            return True, "No description"

        if not has_skills:
            return True, "No skills"

        last_check_time = vacancy.last_seen_at or vacancy.created_at

        if last_check_time:
            if datetime.now(UTC) - last_check_time >= timedelta(days=7):
                return True, "7 days since last_seen_at"

        return False, "Already enriched and recent"

    async def _update_vacancy(self, vacancy: Vacancy, data: dict) -> None:
        if data.get("description"):
            vacancy.description = data["description"]
            logger.info(
                f"Updated description for vacancy {vacancy.id} ({len(data['description'])} chars)"
            )

        if data.get("skills") and (not vacancy.skills or len(vacancy.skills) == 0):
            await self._create_and_attach_skills(vacancy, data["skills"])
            logger.info(f"Created and attached skills for vacancy {vacancy.id}: {data['skills']}")

        if not vacancy.experience and data.get("experience"):
            vacancy.experience = data["experience"]

        if not vacancy.schedule and data.get("schedule"):
            vacancy.schedule = data["schedule"]

        if not vacancy.employment and data.get("employment"):
            vacancy.employment = data["employment"]

        if not vacancy.salary_from and data.get("salary_from"):
            vacancy.salary_from = data["salary_from"]

        if not vacancy.salary_to and data.get("salary_to"):
            vacancy.salary_to = data["salary_to"]

    async def _create_and_attach_skills(self, vacancy: Vacancy, skill_names: list[str]) -> None:
        skills = await self.skill_repository.get_or_create_many(skill_names)

        for skill in skills:
            if skill not in vacancy.skills:
                vacancy.skills.append(skill)
                logger.debug(f"Attached skill '{skill.name}' to vacancy {vacancy.id}")

    async def enrich_vacancy_data(self, vacancy_id: str) -> dict[str, Any] | None:
        data = await self.parser.get_vacancy(vacancy_id)
        if not data:
            return None

        description = data.get("description", "")

        skills = [skill["name"] for skill in data.get("key_skills", []) if skill.get("name")]

        salary_data = data.get("salary", {})
        salary_from = salary_data.get("from") if salary_data else None
        salary_to = salary_data.get("to") if salary_data else None

        return {
            "description": description,
            "skills": skills,
            "experience": data.get("experience", {}).get("name"),
            "schedule": data.get("schedule", {}).get("name"),
            "employment": data.get("employment", {}).get("name"),
            "salary_from": salary_from,
            "salary_to": salary_to,
            "work_format": (
                data.get("work_format", [{}])[0].get("name") if data.get("work_format") else None
            ),
        }
