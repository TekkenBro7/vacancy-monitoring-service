from datetime import datetime

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.core.config import wargaming_config
from src.core.logger import logger
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.wargaming.wargaming_parser import WargamingParser


class WargamingVacancyService(BaseVacancyService):
    def __init__(self, import_service: ParserImportService):
        super().__init__(import_service)
        self.parser = WargamingParser()

    async def run(
        self,
        query: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> None:
        logger.info("Wargaming: starting vacancy parsing")

        if from_date or to_date:
            logger.warning(
                "Wargaming: date filtering not supported, ignoring from_date=%s, to_date=%s",
                from_date,
                to_date,
            )

        if query:
            logger.warning(
                "Wargaming: query filtering not supported, ignoring query=%s",
                query,
            )

        total = 0

        async for batch_vacancies in self.parser.stream_vacancies():
            payload = [v.to_dict() for v in batch_vacancies]

            await _import_vacancies_batch(payload, wargaming_config.WARGAMING_SOURCE_NAME)

            total += len(batch_vacancies)

            logger.debug(
                "Wargaming: sent %s vacancies to import (total: %s)",
                len(batch_vacancies),
                total,
            )

        logger.info("Wargaming: finished parsing → total %s vacancies", total)
