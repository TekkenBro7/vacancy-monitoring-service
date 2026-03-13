from datetime import datetime, timedelta

from src.core.config import hh_config
from src.core.logger import logger
from src.parsers.hh_ru.hh_parser import HHParser


class HHVacancyService:
    def __init__(self):
        self.parser = HHParser()

    async def parse_range(self, query: str | None, start: datetime, end: datetime):
        result = await self.parser.search_vacancies(query, start, end)

        if isinstance(result, int):
            total = result

            logger.info(f"Range {start} - {end}, found {total}")

            if total >= hh_config.HH_MAX_TOTAL:
                mid = start + (end - start) / 2

                if mid <= start:
                    logger.warning(f"Cannot split further {start}-{end}")
                    return []

                first_half = await self.parse_range(query, start, mid)
                second_half = await self.parse_range(query, mid, end)

                return first_half + second_half

        return result

    async def run(self, query: str | None, from_date: datetime, to_date: datetime):
        current = from_date
        delta = timedelta(days=1)

        all_results = []

        while current < to_date:
            next_day = current + delta

            results = await self.parse_range(query, current, next_day)

            all_results.extend(results)

            logger.info(f"Completed parsing {current.date()} -> {len(results)} vacancies")

            current = next_day

        logger.info(f"Total vacancies collected: {len(all_results)}")

        return all_results
