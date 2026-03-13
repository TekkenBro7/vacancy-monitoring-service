import hashlib
from datetime import UTC, datetime

from src.core.config import hh_config
from src.core.logger import logger
from src.database.repositories.city_repository import CityRepository
from src.database.repositories.company_repository import CompanyRepository
from src.database.repositories.currency_repository import CurrencyRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Company, Vacancy
from src.parsers.base.parser_result import ParserVacancyResult


def make_fingerprint(v: ParserVacancyResult):
    raw = f"{v.title}_{v.company_name}_{v.city}"
    return hashlib.sha256(raw.lower().encode()).hexdigest()


class ParserImportService:
    def __init__(
        self,
        vacancy_repo: VacancyRepository,
        company_repo: CompanyRepository,
        city_repo: CityRepository,
        currency_repo: CurrencyRepository,
        source_repo: SourceRepository,
    ):
        self.vacancy_repo = vacancy_repo
        self.company_repo = company_repo
        self.city_repo = city_repo
        self.currency_repo = currency_repo
        self.source_repo = source_repo

    async def import_vacancy(self, vacancy: ParserVacancyResult):
        now = datetime.now(UTC)

        logger.debug(f"Importing vacancy {vacancy.title} ({vacancy.external_id})")

        # source
        source = await self.source_repo.get_by_name(hh_config.HH_SOURCE_NAME)

        # company
        company = await self.company_repo.get_by_name(vacancy.company_name)

        if not company:
            logger.info(f"Creating new company: {vacancy.company_name}")
            company = await self.company_repo.create(Company(name=vacancy.company_name))

        # currency
        currency = None
        if vacancy.currency:
            currency = await self.currency_repo.get_by_code(vacancy.currency)

        # city
        city = None
        if vacancy.city:
            city = await self.city_repo.get_by_name(vacancy.city)

        fingerprint = make_fingerprint(vacancy)

        exists = await self.vacancy_repo.get_by_source_and_external_id(
            source.id, vacancy.external_id
        )

        if exists:
            if not exists.is_active:
                logger.info(f"Reactivating vacancy {vacancy.external_id}")

                exists.title = vacancy.title
                exists.description = vacancy.description
                exists.salary_from = vacancy.salary_from
                exists.salary_to = vacancy.salary_to
                exists.experience = vacancy.experience
                exists.employment = vacancy.employment
                exists.schedule = vacancy.schedule
                exists.published_at = vacancy.published_at
                exists.vacancy_url = vacancy.vacancy_url
                exists.is_remote = vacancy.is_remote
                exists.is_active = True
                exists.last_seen_at = now
                exists.fingerprint = fingerprint

                await self.vacancy_repo.update(exists)

            else:
                logger.debug(f"Vacancy already exists, updating last_seen: {vacancy.external_id}")

                exists.last_seen_at = now
                await self.vacancy_repo.update(exists)

            return

        exists_hash = await self.vacancy_repo.get_by_fingerprint(fingerprint)

        if exists_hash:
            logger.info(f"Duplicate vacancy detected by fingerprint: {vacancy.title}")

            exists_hash.last_seen_at = now
            await self.vacancy_repo.update(exists_hash)

            return

        logger.info(f"Creating new vacancy: {vacancy.title} ({vacancy.company_name})")

        await self.vacancy_repo.create(
            Vacancy(
                title=vacancy.title,
                description=vacancy.description,
                salary_from=vacancy.salary_from,
                salary_to=vacancy.salary_to,
                external_id=vacancy.external_id,
                experience=vacancy.experience,
                employment=vacancy.employment,
                schedule=vacancy.schedule,
                created_at_source=vacancy.created_at,
                published_at=vacancy.published_at,
                company_id=company.id,
                source_id=source.id,
                currency_id=currency.id if currency else None,
                location_id=city.id if city else None,
                vacancy_url=vacancy.vacancy_url,
                is_remote=vacancy.is_remote,
                fingerprint=fingerprint,
                is_active=True,
                last_seen_at=now,
            )
        )
