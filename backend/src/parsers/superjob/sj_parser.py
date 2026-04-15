import asyncio
from datetime import UTC, datetime
from random import uniform
from typing import Any

import aiohttp
from fastapi import status

from src.core.config import super_job_config
from src.core.enums import SJPlaceOfWork
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult


class SJParser:
    SJ_EDUCATION_MAP = {
        0: None,
        2: "Высшее",
        3: "Неполное высшее",
        4: "Средне-специальное",
        5: "Среднее",
        6: "Учащийся",
    }

    SJ_CURRENCY_MAP = {
        "rub": "RUR",
        "usd": "USD",
        "eur": "EUR",
        "uah": "UAH",
        "byn": "BYR",
        "kzt": "KZT",
        "uzs": "UZS",
        "azn": "AZN",
    }

    def __init__(self) -> None:
        self._timeout = aiohttp.ClientTimeout(total=super_job_config.SJ_TIMEOUT)
        self.headers = {
            "X-Api-App-Id": super_job_config.SJ_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        session: aiohttp.ClientSession,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        for attempt in range(super_job_config.SJ_RETRIES):
            try:
                await asyncio.sleep(uniform(0.2, 0.5))

                async with session.get(url, params=params, timeout=self._timeout) as resp:
                    if resp.status == status.HTTP_503_SERVICE_UNAVAILABLE:
                        logger.warning("SJ 503 rate limit! Backoff %ss", 60 * (attempt + 1))
                        await asyncio.sleep(60 * (attempt + 1))
                        continue

                    if resp.status == status.HTTP_429_TOO_MANY_REQUESTS:
                        logger.warning("SJ 429 too many requests! Backoff %ss", 30 * (attempt + 1))
                        await asyncio.sleep(30 * (attempt + 1))
                        continue

                    if resp.status != status.HTTP_200_OK:
                        text = await resp.text()
                        logger.warning(
                            "SJ API bad status %s: %s",
                            resp.status,
                            text[:200],
                        )
                        raise Exception(f"Bad status {resp.status}")

                    return await resp.json()

            except TimeoutError:
                logger.warning("SJ API timeout (attempt %s)", attempt + 1)
            except aiohttp.ClientError as e:
                logger.warning("SJ API connection error: %s", e)

        raise Exception("SJ API request failed after retries")

    def _build_params(
        self,
        page: int,
        query: str | None,
        date_from: datetime,
        date_to: datetime,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "page": page,
            "count": super_job_config.SJ_PER_PAGE,
            "date_published_from": int(date_from.timestamp()),
            "date_published_to": int(date_to.timestamp()),
            "order_field": "date",
            "order_direction": "desc",
        }
        if query:
            params["keyword"] = query
        return params

    async def search_vacancies(
        self,
        query: str | None,
        date_from: datetime,
        date_to: datetime,
    ) -> int:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = self._build_params(0, query, date_from, date_to)
            data = await self._request(session, super_job_config.SJ_BASE_URL, params)
            total = data.get("total", 0)
            logger.debug(
                "SJ search %s - %s: total=%s",
                date_from,
                date_to,
                total,
            )
            return int(total)

    async def fetch_all_vacancies(
        self,
        query: str | None,
        date_from: datetime,
        date_to: datetime,
    ) -> list[ParserVacancyResult]:
        all_vacancies: list[ParserVacancyResult] = []

        async with aiohttp.ClientSession(headers=self.headers) as session:
            page = 0

            while page < super_job_config.SJ_MAX_PAGES:
                params = self._build_params(page, query, date_from, date_to)
                data = await self._request(session, super_job_config.SJ_BASE_URL, params)

                objects = data.get("objects", [])
                more = data.get("more", False)
                total = data.get("total", 0)

                if not objects:
                    break

                parsed = [self._parse_vacancy(v) for v in objects]
                all_vacancies.extend(parsed)

                logger.debug(
                    "SJ page %s parsed (%s items, collected=%s, total=%s)",
                    page + 1,
                    len(objects),
                    len(all_vacancies),
                    total,
                )

                if not more:
                    break

                page += 1

        logger.debug(
            "SJ fetched all vacancies from %s to %s: %s items",
            date_from,
            date_to,
            len(all_vacancies),
        )
        return all_vacancies

    def _parse_education(self, education_data: dict | None) -> str | None:
        if not education_data:
            return None

        education_id = education_data.get("id")

        if education_id in self.SJ_EDUCATION_MAP:
            return self.SJ_EDUCATION_MAP[education_id]

        title = education_data.get("title", "")
        if title and title.lower() != "не имеет значения":
            return title.capitalize()

        return None

    def _normalize_currency(self, currency: str | None) -> str | None:
        if not currency:
            return None

        normalized = currency.lower().strip()
        return self.SJ_CURRENCY_MAP.get(normalized, currency.upper())

    def _parse_vacancy(self, v: dict[str, Any]) -> ParserVacancyResult:
        town = v.get("town") or {}
        experience = v.get("experience") or {}
        type_of_work = v.get("type_of_work") or {}
        place_of_work = v.get("place_of_work") or {}
        client = v.get("client") or {}

        is_remote = place_of_work.get("id") == SJPlaceOfWork.REMOTE

        description_parts = []
        if v.get("work"):
            description_parts.append(f"Обязанности: {v['work']}")
        if v.get("candidat"):
            description_parts.append(f"Требования: {v['candidat']}")
        if v.get("compensation"):
            description_parts.append(f"Условия: {v['compensation']}")
        description = "\n\n".join(description_parts) if description_parts else None

        published_at = None
        if v.get("date_published"):
            published_at = datetime.fromtimestamp(v["date_published"], tz=UTC)

        salary_from = v.get("payment_from") or None
        salary_to = v.get("payment_to") or None
        if salary_from == 0:
            salary_from = None
        if salary_to == 0:
            salary_to = None

        education = self._parse_education(v.get("education"))
        currency = self._normalize_currency(v.get("currency"))

        return ParserVacancyResult(
            external_id=str(v.get("id")),
            title=v.get("profession", ""),
            description=description,
            company_name=v.get("firm_name") or client.get("title"),
            company_external_id=str(client.get("id")) if client.get("id") else None,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            city=town.get("title"),
            address=v.get("address"),
            experience=experience.get("title"),
            education=education,
            employment=type_of_work.get("title"),
            schedule=None,
            is_remote=is_remote,
            published_at=published_at,
            internship=None,
            created_at=None,
            vacancy_url=v.get("link"),
        )
