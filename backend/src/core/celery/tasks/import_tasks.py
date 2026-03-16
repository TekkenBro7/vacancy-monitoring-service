import asyncio

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.database.repositories.city_repository import CityRepository
from src.database.repositories.company_repository import CompanyRepository
from src.database.repositories.currency_repository import CurrencyRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.vacancy_repository import VacancyRepository
from src.database.session import async_session_maker
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.services.parser_import_service import ParserImportService


@celery_app.task(name="import_vacancies_batch", queue="import_queue")
def import_vacancies_batch(vacancies_data: list[dict]) -> None:
    asyncio.run(_import_vacancies_batch(vacancies_data))


async def _import_vacancies_batch(vacancies_data: list[dict]) -> None:
    async with async_session_maker() as session:
        import_service = ParserImportService(
            vacancy_repo=VacancyRepository(session),
            company_repo=CompanyRepository(session),
            city_repo=CityRepository(session),
            currency_repo=CurrencyRepository(session),
            source_repo=SourceRepository(session),
        )

        vacancies = [ParserVacancyResult(**item) for item in vacancies_data]
        await import_service.import_batch(vacancies)

        logger.info("Imported batch with %s vacancies", len(vacancies))