from datetime import datetime

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.core.config import telegram_config
from src.core.logger import logger
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.telegram.telegram_parser import TelegramParser


class TelegramVacancyService(BaseVacancyService):
    def __init__(
        self,
        import_service: ParserImportService,
    ):
        super().__init__(import_service)
        self.channel = telegram_config.TELEGRAM_CHANNEL_NAME
        self.parser = TelegramParser()

    async def _import_vacancies(
        self,
        from_date: datetime,
        to_date: datetime,
    ) -> int:
        total = 0

        async for vacancies in self.parser.stream_vacancies(
            channel=self.channel,
            from_date=from_date,
            to_date=to_date,
        ):
            if not vacancies:
                continue

            payload = [v.to_dict() for v in vacancies]
            await _import_vacancies_batch(payload, telegram_config.TELEGRAM_SOURCE_NAME)

            total += len(vacancies)

            logger.info(
                "Telegram %s: sent %d vacancies to import (total: %d)",
                self.channel,
                len(vacancies),
                total,
            )

        return total

    async def run(
        self,
        query: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> None:
        if query:
            logger.warning(
                "Telegram: query filtering not supported, ignoring query=%s",
                query,
            )

        if from_date is None or to_date is None:
            raise ValueError("from_date and to_date are required")

        logger.info(
            "Telegram: starting %s [%s → %s]",
            self.channel,
            from_date.date(),
            to_date.date(),
        )

        async with self.parser:
            total = await self._import_vacancies(from_date, to_date)

        logger.info(
            "Telegram finished: %s → %d vacancies",
            self.channel,
            total,
        )
