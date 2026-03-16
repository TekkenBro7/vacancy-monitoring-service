from datetime import UTC, datetime

from src.core.config import hh_config
from src.core.logger import logger
from src.database.repositories.city_repository import CityRepository
from src.database.repositories.company_repository import CompanyRepository
from src.database.repositories.currency_repository import CurrencyRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Company, Vacancy
from src.models.locations import City
from src.parsers.base.parser_result import ParserVacancyResult
from src.utils.hash_vacancy import make_fingerprint


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

        self.company_cache: dict[str, Company] = {}
        self.city_cache: dict[str, int | None] = {}
        self.currency_cache: dict[str, int | None] = {}
        self.source_cache = None


    async def import_batch(self, vacancies: list[ParserVacancyResult]):
        for vacancy in vacancies:
            await self.import_vacancy(vacancy)

    async def import_vacancy(self, vacancy: ParserVacancyResult):
        now = datetime.now(UTC)

        logger.debug(
            "Importing vacancy %s (%s)",
            vacancy.title,
            vacancy.external_id,
        )

        source = await self._get_source()
        company = await self._get_company(vacancy.company_name)
        currency_id = await self._get_currency(vacancy.currency)
        city_id = await self._get_city(vacancy.city)

        fingerprint = make_fingerprint(vacancy)

        exists = await self.vacancy_repo.get_by_source_and_external_id(
            source.id, vacancy.external_id
        )

        if exists:
            return await self._handle_existing_vacancy(
                exists,
                vacancy,
                company.id,
                source.id,
                currency_id,
                city_id,
                fingerprint,
                now,
            )

        duplicate = await self.vacancy_repo.get_by_fingerprint(fingerprint)

        if duplicate:
            logger.info(
                "Duplicate vacancy detected by fingerprint: %s",
                vacancy.title,
            )

            duplicate.last_seen_at = now
            await self.vacancy_repo.update(duplicate)
            return

        await self._create_vacancy(
            vacancy,
            company.id,
            source.id,
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
    ):
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

        logger.debug(
            "Vacancy already exists, updating last_seen: %s",
            exists.external_id,
        )

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
        model.employment = vacancy.employment
        model.schedule = vacancy.schedule
        model.published_at = vacancy.published_at
        model.company_id = company_id
        model.source_id = source_id
        model.currency_id = currency_id
        model.location_id = city_id
        model.vacancy_url = vacancy.vacancy_url
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
        logger.debug(
            "Creating new vacancy: %s (%s)",
            vacancy.title,
            vacancy.company_name,
        )

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

    async def _get_source(self):
        if self.source_cache:
            return self.source_cache

        source = await self.source_repo.get_by_name(hh_config.HH_SOURCE_NAME)
        self.source_cache = source
        return source

    async def _get_company(self, name: str) -> Company:
        if name in self.company_cache:
            return self.company_cache[name]

        company = await self.company_repo.get_by_name(name)

        if not company:
            logger.info("Creating new company: %s", name)
            company = await self.company_repo.create(Company(name=name))

        self.company_cache[name] = company
        return company

    async def _get_city(self, name: str | None):
        if not name:
            return None

        if name in self.city_cache:
            return self.city_cache[name]

        city = await self.city_repo.get_by_name(name)

        if not city:
            logger.info("Creating new city: %s", name)
            city = await self.city_repo.create(City(name=name))

        self.city_cache[name] = city.id
        return city.id

    async def _get_currency(self, code: str | None):
        if not code:
            return None

        if code in self.currency_cache:
            return self.currency_cache[code]

        currency = await self.currency_repo.get_by_code(code)

        if not currency:
            self.currency_cache[code] = None
            return None

        self.currency_cache[code] = currency.id
        return currency.id
