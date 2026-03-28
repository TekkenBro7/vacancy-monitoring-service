from datetime import UTC, datetime

from src.core.logger import logger
from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Vacancy
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.services.redis_cache_service import RedisCacheService
from src.utils.hash_vacancy import make_fingerprint


class ParserImportService:
    def __init__(
        self,
        vacancy_repo: VacancyRepository,
        cache_service: RedisCacheService,
    ):
        self.vacancy_repo = vacancy_repo
        self.cache = cache_service

    async def import_batch(
        self,
        vacancies: list[ParserVacancyResult],
        source_name: str,
    ) -> None:
        for vacancy in vacancies:
            await self.import_vacancy(vacancy, source_name)

    async def import_vacancy(
        self,
        vacancy: ParserVacancyResult,
        source_name: str,
    ) -> None:
        now = datetime.now(UTC)

        logger.debug("Importing vacancy %s (%s)", vacancy.title, vacancy.external_id)

        source_id = await self.cache.get_source_id(source_name)
        if not source_id:
            logger.error("Source not found: %s", source_name)
            return

        company_id = await self.cache.get_company_id(vacancy.company_name)
        currency_id = await self.cache.get_currency_id(vacancy.currency)
        city_id = await self.cache.get_city_id(vacancy.city)

        fingerprint = make_fingerprint(vacancy)

        exists = await self.vacancy_repo.get_by_source_and_external_id(
            source_id, vacancy.external_id
        )

        if exists:
            return await self._handle_existing_vacancy(
                exists,
                vacancy,
                company_id,
                source_id,
                currency_id,
                city_id,
                fingerprint,
                now,
            )

        duplicate = await self.vacancy_repo.get_by_fingerprint(fingerprint)

        if duplicate:
            duplicate.last_seen_at = now
            await self.vacancy_repo.update(duplicate)
            return

        await self._create_vacancy(
            vacancy,
            company_id,
            source_id,
            currency_id,
            city_id,
            fingerprint,
            now,
        )

    async def _handle_existing_vacancy(
        self,
        exists: Vacancy,
        vacancy: ParserVacancyResult,
        company_id: int,
        source_id: int,
        currency_id: int | None,
        city_id: int | None,
        fingerprint: str,
        now: datetime,
    ) -> None:
        if not exists.is_active:
            logger.info("Reactivating vacancy %s", vacancy.external_id)

            self._apply_vacancy_data(
                exists,
                vacancy,
                company_id,
                source_id,
                currency_id,
                city_id,
                fingerprint,
            )

            exists.is_active = True
            exists.last_seen_at = now

            await self.vacancy_repo.update(exists)
            return

        exists.last_seen_at = now
        await self.vacancy_repo.update(exists)

    def _apply_vacancy_data(
        self,
        model: Vacancy,
        vacancy: ParserVacancyResult,
        company_id: int,
        source_id: int,
        currency_id: int | None,
        city_id: int | None,
        fingerprint: str,
    ) -> None:
        model.title = vacancy.title
        model.description = vacancy.description
        model.salary_from = vacancy.salary_from
        model.salary_to = vacancy.salary_to
        model.experience = vacancy.experience
        model.education = vacancy.education
        model.employment = vacancy.employment
        model.schedule = vacancy.schedule
        model.published_at = vacancy.published_at
        model.company_id = company_id
        model.source_id = source_id
        model.currency_id = currency_id
        model.location_id = city_id
        model.vacancy_url = vacancy.vacancy_url
        model.address = vacancy.address
        model.is_remote = vacancy.is_remote
        model.fingerprint = fingerprint
        model.internship = vacancy.internship

    async def _create_vacancy(
        self,
        vacancy: ParserVacancyResult,
        company_id: int,
        source_id: int,
        currency_id: int | None,
        city_id: int | None,
        fingerprint: str,
        now: datetime,
    ) -> None:
        await self.vacancy_repo.create(
            Vacancy(
                title=vacancy.title,
                description=vacancy.description,
                salary_from=vacancy.salary_from,
                salary_to=vacancy.salary_to,
                external_id=vacancy.external_id,
                experience=vacancy.experience,
                education=vacancy.education,
                employment=vacancy.employment,
                schedule=vacancy.schedule,
                address=vacancy.address,
                created_at_source=vacancy.created_at,
                published_at=vacancy.published_at,
                company_id=company_id,
                source_id=source_id,
                currency_id=currency_id,
                location_id=city_id,
                vacancy_url=vacancy.vacancy_url,
                is_remote=vacancy.is_remote,
                fingerprint=fingerprint,
                internship=vacancy.internship,
                is_active=True,
                last_seen_at=now,
            )
        )
