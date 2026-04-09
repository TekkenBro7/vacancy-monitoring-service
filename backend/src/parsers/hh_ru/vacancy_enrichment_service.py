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
    ENRICHMENT_INTERVAL_DAYS = 3

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.skill_repository = SkillRepository(Skill, self.db)
        self.parser = HHParser()

    async def enrich_vacancy_if_needed(self, vacancy: Vacancy) -> Vacancy:
        should_enrich, reason = self._should_enrich(vacancy)

        if not should_enrich:
            logger.warning(f"Vacancy {vacancy.id} does not need enrichment: {reason}")
            return vacancy

        logger.info(
            f"Enriching vacancy {vacancy.id} from HH.ru API "
            f"(external_id: {vacancy.external_id}). Reason: {reason}"
        )

        enriched_data = await self.enrich_vacancy_data(vacancy.external_id)

        if enriched_data is None:
            logger.warning(f"Vacancy {vacancy.id} not found in HH.ru API - marking as inactive")
            vacancy.is_active = False
            vacancy.last_enriched_at = datetime.now(UTC)
        else:
            logger.info(
                f"Successfully enriched vacancy {vacancy.id} "
                f"with {len(enriched_data.get('skills', []))} skills"
            )
            await self._update_vacancy(vacancy, enriched_data)
            vacancy.is_active = enriched_data.get("is_active", True)
            vacancy.last_enriched_at = datetime.now(UTC)

        return vacancy

    def _should_enrich(self, vacancy: Vacancy) -> tuple[bool, str]:
        if not vacancy.source:
            return False, "No source"

        if vacancy.source.name != HHConfig.HH_SOURCE_NAME:
            return False, f"Source is {vacancy.source.name}, not HeadHunter"

        if not vacancy.external_id:
            return False, "No external_id"

        if not vacancy.last_enriched_at:
            description = vacancy.description or ""
            if len(description.strip()) == 0:
                return True, "Never enriched and no description"
            return True, "Never enriched"

        time_since_enrichment = datetime.now(UTC) - vacancy.last_enriched_at

        if time_since_enrichment >= timedelta(days=self.ENRICHMENT_INTERVAL_DAYS):
            return True, f"{self.ENRICHMENT_INTERVAL_DAYS} days since last enrichment"

        return False, "Recently enriched"

    async def _update_vacancy(self, vacancy: Vacancy, data: dict) -> None:
        if data.get("description"):
            vacancy.description = data["description"]
            logger.debug(
                f"Updated description for vacancy {vacancy.id} ({len(data['description'])} chars)"
            )

        if data.get("skills"):
            await self._update_skills(vacancy, data["skills"])

        if data.get("experience"):
            vacancy.experience = data["experience"]

        if data.get("schedule"):
            vacancy.schedule = data["schedule"]

        if data.get("employment"):
            vacancy.employment = data["employment"]

        if data.get("salary_from") is not None:
            vacancy.salary_from = data["salary_from"]

        if data.get("salary_to") is not None:
            vacancy.salary_to = data["salary_to"]

    async def _update_skills(self, vacancy: Vacancy, skill_names: list[str]) -> None:
        if not skill_names:
            return

        skills = await self.skill_repository.get_or_create_many(skill_names)
        existing_skill_ids = {skill.id for skill in vacancy.skills}

        added_count = 0
        for skill in skills:
            if skill.id not in existing_skill_ids:
                vacancy.skills.append(skill)
                added_count += 1

        if added_count > 0:
            logger.debug(f"Added {added_count} new skills to vacancy {vacancy.id}")

    async def enrich_vacancy_data(self, vacancy_id: str) -> dict[str, Any] | None:
        data = await self.parser.get_vacancy(vacancy_id)

        if not data:
            return None

        is_archived = data.get("archived", False)
        is_active = not is_archived

        description = data.get("description", "")
        skills = [skill["name"] for skill in data.get("key_skills", []) if skill.get("name")]

        salary_data = data.get("salary") or {}
        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")

        return {
            "description": description,
            "skills": skills,
            "experience": data.get("experience", {}).get("name"),
            "schedule": data.get("schedule", {}).get("name"),
            "employment": data.get("employment", {}).get("name"),
            "salary_from": salary_from,
            "salary_to": salary_to,
            "is_active": is_active,
            "work_format": (
                data.get("work_format", [{}])[0].get("name") if data.get("work_format") else None
            ),
        }
