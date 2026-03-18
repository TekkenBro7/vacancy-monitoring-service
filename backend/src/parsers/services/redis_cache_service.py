import redis.asyncio as redis

from src.core.logger import logger
from src.database.repositories.city_repository import CityRepository
from src.database.repositories.company_repository import CompanyRepository
from src.database.repositories.currency_repository import CurrencyRepository
from src.database.repositories.source_repository import SourceRepository
from src.models.companies import Company
from src.models.locations import City
from src.utils.redis_keys import RedisKeys


class RedisCacheService:
    TTL_CACHE = 24 * 3600
    TTL_NEGATIVE = 10 * 60

    def __init__(
        self,
        redis_client: redis.Redis,
        company_repo: CompanyRepository,
        city_repo: CityRepository,
        currency_repo: CurrencyRepository,
        source_repo: SourceRepository,
    ):
        self.redis = redis_client
        self.keys = RedisKeys()
        self.company_repo = company_repo
        self.city_repo = city_repo
        self.currency_repo = currency_repo
        self.source_repo = source_repo

    async def _get(self, key: str) -> str | None:
        try:
            return await self.redis.get(key)
        except redis.RedisError as e:
            logger.warning("Redis GET error %s: %s", key, e)
            return None

    async def _set(self, key: str, value: str, ttl: int) -> None:
        try:
            await self.redis.set(key, value, ex=ttl)
        except redis.RedisError as e:
            logger.warning("Redis SET error %s: %s", key, e)

    async def get_source_id(self, source_name: str) -> int | None:
        key = self.keys.source_key(source_name)

        cached = await self._get(key)
        if cached:
            if cached == "-1":
                return None
            return int(cached)

        source = await self.source_repo.get_by_name(source_name)

        if source:
            await self._set(key, str(source.id), self.TTL_CACHE)
            return source.id

        await self._set(key, "-1", self.TTL_NEGATIVE)
        return None

    async def get_company_id(self, name: str | None) -> int:
        name = (name or "Unknown").strip()
        key = self.keys.company_key(name)

        cached = await self._get(key)
        if cached:
            return int(cached)

        company = await self.company_repo.get_by_name(name)
        if not company:
            logger.debug("Creating company: %s", name)
            company = await self.company_repo.create(Company(name=name))

        await self._set(key, str(company.id), self.TTL_CACHE)
        return company.id

    async def get_city_id(self, name: str | None) -> int | None:
        if not name:
            return None

        name = name.strip()
        key = self.keys.city_key(name)

        cached = await self._get(key)
        if cached:
            return int(cached)

        city = await self.city_repo.get_by_name(name)
        if not city:
            logger.debug("Creating city: %s", name)
            city = await self.city_repo.create(City(name=name))

        await self._set(key, str(city.id), self.TTL_CACHE)
        return city.id

    async def get_currency_id(self, code: str | None) -> int | None:
        if not code:
            return None

        code = code.strip().upper()
        key = self.keys.currency_key(code)

        cached = await self._get(key)
        if cached:
            if cached == "-1":
                return None
            return int(cached)

        currency = await self.currency_repo.get_by_code(code)

        if currency:
            await self._set(key, str(currency.id), self.TTL_CACHE)
            return currency.id

        await self._set(key, "-1", self.TTL_NEGATIVE)

        return None
