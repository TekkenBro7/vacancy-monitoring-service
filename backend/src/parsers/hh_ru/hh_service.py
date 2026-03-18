from datetime import datetime, timedelta

from src.core.celery.tasks.import_tasks import import_vacancies_batch
from src.core.config import hh_config
from src.core.logger import logger
from src.parsers.hh_ru.hh_parser import HHParser
from src.parsers.services.parser_import_service import ParserImportService


class HHVacancyService:
    def __init__(self, import_service: ParserImportService):
        self.parser = HHParser()
        self.import_service = import_service

    async def _import_range(self, query: str | None, start: datetime, end: datetime) -> int:
        total = 0

        async for batch in self.parser.stream_vacancies(query, start, end):
            payload = [v.to_dict() for v in batch]
            import_vacancies_batch.delay(payload, hh_config.HH_SOURCE_NAME)
            total += len(batch)

        logger.info("Range %s - %s → imported %s", start, end, total)
        return total

    async def _parse_range(self, query: str | None, start: datetime, end: datetime) -> int:
        total = await self.parser.search_vacancies(query, start, end)

        if total >= hh_config.HH_MAX_TOTAL:
            mid = start + (end - start) / 2

            if mid <= start:
                logger.warning("Cannot split further %s-%s", start, end)
                return 0

            logger.info(
                "Range %s - %s found %s vacancies, splitting",
                start,
                end,
                total,
            )

            left = await self._parse_range(query, start, mid)
            right = await self._parse_range(query, mid, end)

            return left + right

        return await self._import_range(query, start, end)

    async def run(self, query: str | None, from_date: datetime, to_date: datetime) -> None:
        current = from_date
        step = timedelta(days=1)

        total = 0

        while current < to_date:
            next_day = current + step

            imported = await self._parse_range(query, current, next_day)
            total += imported

            logger.info("%s → imported %s", current.date(), imported)

            current = next_day

        logger.info("Finished parsing → total imported %s", total)
