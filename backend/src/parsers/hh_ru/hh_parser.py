import asyncio
from datetime import datetime

import aiohttp

from src.core.config import hh_config
from src.core.enums import HHWorkFormat
from src.core.logger import logger
from src.parsers.base.base_parser import BaseParser
from src.parsers.base.parser_result import ParserVacancyResult
from src.utils.datetime_utils import parse_hh_datetime


class HHParser(BaseParser):
    async def _request(self, session: aiohttp.ClientSession, url: str, params: dict):
        for attempt in range(hh_config.HH_RETRIES):
            try:
                async with session.get(url, params=params, timeout=hh_config.HH_TIMEOUT) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"HH API bad status {resp.status}: {text[:200]}")
                        raise Exception(f"Bad status {resp.status}")

                    return await resp.json()

            except TimeoutError:
                logger.warning(f"HH API timeout (attempt {attempt + 1})")

            except aiohttp.ClientError as e:
                logger.warning(f"HH API connection error: {e}")

            await asyncio.sleep(2**attempt)

        raise Exception("HH API request failed after retries")

    async def search_vacancies(
        self,
        query: str | None,
        date_from: datetime,
        date_to: datetime,
    ) -> list[ParserVacancyResult] | int:
        params = {
            "page": 0,
            "per_page": 100,
            "date_from": date_from.strftime("%Y-%m-%dT%H:%M:%S"),
            "date_to": date_to.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        if query:
            params["text"] = query

        async with aiohttp.ClientSession() as session:
            data = await self._request(session, hh_config.HH_BASE_URL, params)

            found = data.get("found", 0)

            logger.info(f"HHParser range {date_from} - {date_to} → found={found}")

            if found > hh_config.HH_MAX_TOTAL:
                return found

            results: list[ParserVacancyResult] = []

            pages = data.get("pages", 0)

            items = data.get("items", [])

            for v in items:
                results.append(self._parse_vacancy(v))

            logger.info(f"HHParser page 1/{pages} parsed ({len(items)} items)")

            for page in range(1, pages):
                params["page"] = page

                data = await self._request(session, hh_config.HH_BASE_URL, params)
                items = data.get("items", [])

                for v in items:
                    results.append(self._parse_vacancy(v))

                logger.info(f"HHParser page {page + 1}/{pages} parsed ({len(items)} items)")

            return results

    def _parse_vacancy(self, v: dict) -> ParserVacancyResult:
        salary = v.get("salary") or {}
        employer = v.get("employer") or {}
        snippet = v.get("snippet") or {}

        return ParserVacancyResult(
            external_id=v["id"],
            title=v.get("name"),
            description=snippet.get("responsibility"),
            company_name=employer.get("name", "Unknown"),
            company_external_id=employer.get("id"),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency"),
            city=(v.get("area") or {}).get("name"),
            experience=(v.get("experience") or {}).get("name"),
            employment=(v.get("employment") or {}).get("name"),
            schedule=(v.get("schedule") or {}).get("name"),
            is_remote=any(
                wf.get("id") == HHWorkFormat.REMOTE for wf in (v.get("work_format") or [])
            ),
            published_at=parse_hh_datetime(v.get("published_at")),
            created_at=parse_hh_datetime(v.get("created_at")),
            vacancy_url=v.get("alternate_url"),
        )
