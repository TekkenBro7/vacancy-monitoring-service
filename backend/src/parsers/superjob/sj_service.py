from datetime import datetime, timedelta

from src.core.celery.tasks.import_tasks import _import_vacancies_batch
from src.core.config import super_job_config
from src.core.logger import logger
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.superjob.sj_parser import SJParser


class SJVacancyService(BaseVacancyService):
    MIN_SPLIT_INTERVAL = 60

    def __init__(self, import_service: ParserImportService):
        super().__init__(import_service)
        self.parser = SJParser()

    async def _import_range(
        self,
        query: str | None,
        start: datetime,
        end: datetime,
    ) -> int:
        vacancies = await self.parser.fetch_all_vacancies(query, start, end)

        if not vacancies:
            logger.debug("SJ no vacancies to import from %s to %s", start, end)
            return 0

        payload = [v.to_dict() for v in vacancies]
        
        await _import_vacancies_batch(payload, super_job_config.SJ_SOURCE_NAME)

        logger.info(
            "SJ imported %s vacancies from %s to %s (single batch)",
            len(vacancies),
            start.isoformat(),
            end.isoformat(),
        )
        return len(vacancies)

    async def _parse_range(
        self,
        query: str | None,
        start: datetime,
        end: datetime,
    ) -> int:
        total = await self.parser.search_vacancies(query, start, end)

        if total == 0:
            logger.debug("SJ no vacancies in range %s - %s", start, end)
            return 0

        if total <= super_job_config.SJ_MAX_TOTAL:
            return await self._import_range(query, start, end)

        start_ts = start.timestamp()
        end_ts = end.timestamp()
        interval = end_ts - start_ts

        if interval < self.MIN_SPLIT_INTERVAL:
            logger.warning(
                "SJ cannot split further: %s - %s (interval=%.1fs, total=%s). "
                "Importing first 480 vacancies.",
                start,
                end,
                interval,
                total,
            )
            return await self._import_range(query, start, end)

        mid_ts = (start_ts + end_ts) / 2
        mid = datetime.fromtimestamp(mid_ts, tz=start.tzinfo)

        logger.info(
            "SJ splitting range %s - %s (total=%s > 480) at %s",
            start.isoformat(),
            end.isoformat(),
            total,
            mid.isoformat(),
        )

        left = await self._parse_range(query, start, mid)
        right = await self._parse_range(query, mid, end)

        return left + right

    async def run(
        self,
        query: str | None,
        from_date: datetime,
        to_date: datetime,
    ) -> None:
        current = from_date
        step = timedelta(days=1)
        total = 0

        while current < to_date:
            next_point = min(current + step, to_date)

            day_imported = await self._parse_range(query, current, next_point)
            total += day_imported

            logger.info(
                "SJ day %s completed: %s vacancies",
                current.date(),
                day_imported,
            )

            current = next_point

        logger.info("SJ finished parsing → total %s vacancies", total)
