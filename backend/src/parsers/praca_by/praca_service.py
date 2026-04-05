from datetime import datetime, timedelta

import httpx

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.core.config import praca_config
from src.core.logger import logger
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.praca_by.praca_parser import PracaByParser
from src.parsers.services.parser_import_service import ParserImportService


class PracaByVacancyService(BaseVacancyService):
    def __init__(self, import_service: ParserImportService):
        super().__init__(import_service)
        self.parser = PracaByParser()

    async def _import_date(
        self,
        client: httpx.AsyncClient,
        target_date: datetime,
    ) -> int:
        total = 0
        page_num = 0

        async for page_vacancies in self.parser.stream_vacancies(client, target_date.date()):
            page_num += 1

            payload = [v.to_dict() for v in page_vacancies]

            await _import_vacancies_batch(payload, praca_config.PRACA_SOURCE_NAME)

            total += len(page_vacancies)

            logger.debug(
                "PracaBy %s page %s: sent %s vacancies (total: %s)",
                target_date.date(),
                page_num,
                len(page_vacancies),
                total,
            )

        return total

    async def run(
        self,
        query: str | None,
        from_date: datetime,
        to_date: datetime,
    ) -> None:
        current = from_date
        step = timedelta(days=1)
        total = 0

        async with httpx.AsyncClient() as client:
            while current < to_date:
                logger.info("PracaBy: scraping %s", current.date())

                imported = await self._import_date(client, current)
                total += imported

                logger.info("PracaBy %s → %s vacancies", current.date(), imported)

                current += step

        logger.info("PracaBy finished parsing → total %s vacancies", total)
