from datetime import datetime

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.core.config import epam_config
from src.core.logger import logger
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.epam.epam_parser import EpamParser
from src.parsers.services.parser_import_service import ParserImportService


class EpamVacancyService(BaseVacancyService):
    def __init__(self, import_service: ParserImportService):
        super().__init__(import_service)
        self.parser = EpamParser()

    async def run(
        self,
        query: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> None:
        logger.info("EPAM: starting vacancy parsing")

        if from_date or to_date:
            logger.warning(
                "EPAM: date filtering is not supported, ignoring from_date=%s, to_date=%s",
                from_date,
                to_date,
            )

        total = 0

        async for page_vacancies in self.parser.stream_vacancies():
            payload = [v.to_dict() for v in page_vacancies]

            await _import_vacancies_batch(payload, epam_config.EPAM_SOURCE_NAME)

            total += len(page_vacancies)

            logger.debug(
                "EPAM: sent %s vacancies to import (total: %s)",
                len(page_vacancies),
                total,
            )

        logger.info("EPAM finished parsing → total %s vacancies", total)
