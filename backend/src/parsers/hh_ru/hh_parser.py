import asyncio
import re
from collections.abc import AsyncGenerator
from datetime import datetime
from random import uniform
from typing import Any

import aiohttp
from fastapi import status

from src.core.config import hh_config
from src.core.enums import HHWorkFormat
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult
from src.utils.datetime_utils import parse_hh_datetime


class HHParser:
    EDUCATION_PATTERNS = [
        # Неполное высшее (проверяем первым, чтобы не перехватило "высшее")
        (re.compile(r"\bнеполное\s+высшее\b", re.IGNORECASE), "Неполное высшее"),
        # Высшее образование
        (
            re.compile(
                r"\bвысшее\s+(?:образование|техническое|профессиональное|медицинское|юридическое|экономическое|педагогическое)\b",
                re.IGNORECASE,
            ),
            "Высшее",
        ),
        (
            re.compile(
                r"\bвысшее\b(?!\s+(?:качество|уровень|требовани|руководств))", re.IGNORECASE
            ),
            "Высшее",
        ),
        # Средне-специальное / среднее профессиональное
        (re.compile(r"\bсредне[\s-]?специальное\b", re.IGNORECASE), "Средне-специальное"),
        (
            re.compile(
                r"\bсреднее\s+(?:специальное|профессиональное|техническое)\b", re.IGNORECASE
            ),
            "Средне-специальное",
        ),
        (
            re.compile(r"\bспо\b", re.IGNORECASE),
            "Средне-специальное",
        ),  # СПО - среднее профессиональное
        # Среднее образование
        (re.compile(r"\bсреднее\s+(?:общее\s+)?образование\b", re.IGNORECASE), "Среднее"),
        (re.compile(r"\bполное\s+среднее\b", re.IGNORECASE), "Среднее"),
        # Без образования / не требуется
        (
            re.compile(
                r"\bобразование\s+не\s+(?:требуется|важно|имеет\s+значения)\b", re.IGNORECASE
            ),
            None,
        ),
        (re.compile(r"\bбез\s+(?:специального\s+)?образования\b", re.IGNORECASE), None),
    ]

    def __init__(self) -> None:
        self._timeout = aiohttp.ClientTimeout(total=hh_config.HH_TIMEOUT)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Referer": "https://hh.ru/",
        }

    async def _request(
        self, session: aiohttp.ClientSession, url: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        for attempt in range(hh_config.HH_RETRIES):
            try:
                await asyncio.sleep(0.35 + uniform(0.3, 0.8))

                async with session.get(url, params=params, timeout=self._timeout) as resp:
                    if resp.status == status.HTTP_403_FORBIDDEN:
                        logger.warning("HH 403! Backoff %ss", 60 * (attempt + 1))
                        await asyncio.sleep(60 * (attempt + 1))
                        continue

                    if resp.status != status.HTTP_200_OK:
                        text = await resp.text()
                        logger.warning(
                            "HH API bad status %s: %s",
                            resp.status,
                            text[:200],
                        )
                        raise Exception(f"Bad status {resp.status}")
                    return await resp.json()
            except TimeoutError:
                logger.warning("HH API timeout (attempt %s)", attempt + 1)
            except aiohttp.ClientError as e:
                logger.warning("HH API connection error: %s", e)
        raise Exception("HH API request failed after retries")

    async def get_vacancy(self, vacancy_id: str) -> dict[str, Any] | None:
        try:
            async with aiohttp.ClientSession(
                headers=self.headers, timeout=self._timeout
            ) as session:
                url = f"{hh_config.HH_BASE_URL}/{vacancy_id}"
                logger.info(f"Fetching HH vacancy {vacancy_id} from {url}")

                async with session.get(url) as response:
                    response_text = await response.text()

                    if response.status == status.HTTP_200_OK:
                        data = await response.json()
                        logger.info(f"Successfully fetched HH vacancy {vacancy_id}")
                        return data
                    elif response.status == status.HTTP_404_NOT_FOUND:
                        logger.warning(f"HH vacancy {vacancy_id} not found (404)")
                        return None
                    elif response.status == status.HTTP_429_TOO_MANY_REQUESTS:
                        logger.error(f"HH API rate limit exceeded for vacancy {vacancy_id}")
                        return None
                    else:
                        logger.error(
                            f"HH API error: {response.status} for vacancy {vacancy_id}. Response: {response_text[:200]}"
                        )
                        return None

        except TimeoutError:
            logger.error(f"Timeout fetching HH vacancy {vacancy_id}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching HH vacancy {vacancy_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching HH vacancy {vacancy_id}: {e}")
            return None

    def _build_params(
        self,
        page: int,
        query: str | None,
        date_from: datetime,
        date_to: datetime,
        per_page: int = 100,
    ) -> dict[str, Any]:
        params = {
            "page": page,
            "per_page": per_page,
            "date_from": date_from.strftime("%Y-%m-%dT%H:%M:%S"),
            "date_to": date_to.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        if query:
            params["text"] = query
        return params

    async def stream_vacancies(
        self, query: str | None, date_from: datetime, date_to: datetime
    ) -> AsyncGenerator[list[ParserVacancyResult], None]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = self._build_params(0, query, date_from, date_to)
            data = await self._request(session, hh_config.HH_BASE_URL, params)

            pages = data.get("pages", 0)
            items = data.get("items", [])
            logger.debug(
                "HH page 1/%s parsed (%s items)",
                pages,
                len(items),
            )
            yield [self._parse_vacancy(v) for v in items]

            for page in range(1, pages):
                params = self._build_params(page, query, date_from, date_to)
                data = await self._request(session, hh_config.HH_BASE_URL, params)
                items = data.get("items", [])
                logger.debug(
                    "HH page %s/%s parsed (%s items)",
                    page + 1,
                    pages,
                    len(items),
                )
                yield [self._parse_vacancy(v) for v in items]

    def _extract_education_from_requirement(self, requirement: str | None) -> str | None:
        if not requirement:
            return None

        for pattern, education_value in self.EDUCATION_PATTERNS:
            if pattern.search(requirement):
                return education_value

        return None

    def _parse_vacancy(self, v: dict[str, Any]) -> ParserVacancyResult:
        area = v.get("area") or {}
        experience = v.get("experience") or {}
        employment = v.get("employment") or {}
        schedule = v.get("schedule") or {}
        salary = v.get("salary") or {}
        employer = v.get("employer") or {}
        snippet = v.get("snippet") or {}
        address = v.get("address") or {}

        education = self._extract_education_from_requirement(snippet.get("requirement"))

        return ParserVacancyResult(
            external_id=v.get("id"),  # type: ignore
            title=v.get("name"),  # type: ignore
            description=snippet.get("responsibility"),
            company_name=employer.get("name", "Unknown"),
            company_external_id=employer.get("id"),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency"),
            city=area.get("name"),
            address=address.get("raw"),
            experience=experience.get("name"),
            education=education,
            employment=employment.get("name"),
            schedule=schedule.get("name"),
            is_remote=any(
                wf.get("id") == HHWorkFormat.REMOTE for wf in (v.get("work_format") or [])
            ),
            published_at=parse_hh_datetime(v.get("published_at")),
            internship=v.get("internship"),
            created_at=parse_hh_datetime(v.get("created_at")),
            vacancy_url=v.get("alternate_url"),
        )

    async def search_vacancies(
        self, query: str | None, date_from: datetime, date_to: datetime
    ) -> int:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = self._build_params(0, query, date_from, date_to, per_page=1)
            data = await self._request(session, hh_config.HH_BASE_URL, params)
            total_found = data.get("found")
            if total_found is None:
                logger.warning(
                    "HH API response missing 'found' field: %s",
                    data,
                )
                return 0
            return int(total_found)
