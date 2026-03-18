from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.city_repository import CityRepository
from src.database.repositories.company_repository import CompanyRepository
from src.database.repositories.currency_repository import CurrencyRepository
from src.database.repositories.source_repository import SourceRepository
from src.database.repositories.vacancy_repository import VacancyRepository
from src.models.companies import Company, Vacancy
from src.models.currencies import Currency
from src.models.locations import City
from src.models.sources import Source
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.services.redis_cache_service import RedisCacheService
from src.core.redis_client import create_redis_client


class ParserServiceFactory:
    @staticmethod
    def create_import_service(session: AsyncSession) -> ParserImportService:        
        company_repo = CompanyRepository(Company, session)
        city_repo = CityRepository(City, session)
        currency_repo = CurrencyRepository(Currency, session)
        source_repo = SourceRepository(Source, session)
        
        import redis.asyncio as redis
        from src.core.config import redis_config
        
        redis_client = redis.from_url(
            redis_config.redis_url,
            decode_responses=True,
        )

        cache_service = RedisCacheService(
            redis_client=redis_client,
            company_repo=company_repo,
            city_repo=city_repo,
            currency_repo=currency_repo,
            source_repo=source_repo,
        )

        return ParserImportService(
            vacancy_repo=VacancyRepository(Vacancy, session),
            cache_service=cache_service,
        )
