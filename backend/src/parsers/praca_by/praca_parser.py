import asyncio
import re
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, timedelta
from random import uniform

import httpx
from fastapi import status
from selectolax.parser import HTMLParser

from src.core.config import praca_config
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult


class PracaByParser:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def _request(self, client: httpx.AsyncClient, url: str) -> str | None:
        for attempt in range(praca_config.PRACA_RETRIES):
            try:
                await asyncio.sleep(praca_config.PRACA_RATE_LIMIT_DELAY + uniform(0.1, 0.3))

                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=praca_config.PRACA_TIMEOUT,
                    follow_redirects=True,
                )

                if response.status_code == status.HTTP_200_OK:
                    return response.text

                if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    logger.warning("PracaBy 429! Backoff %ss", 60 * (attempt + 1))
                    await asyncio.sleep(60 * (attempt + 1))
                    continue

                logger.warning("PracaBy bad status %s for %s", response.status_code, url)

            except httpx.TimeoutException:
                logger.warning("PracaBy timeout (attempt %s) for %s", attempt + 1, url)
            except httpx.HTTPError as e:
                logger.warning("PracaBy HTTP error: %s", e)

        return None

    def _parse_relative_date(self, date_text: str) -> date:
        date_text = date_text.lower().strip()
        today = datetime.now(UTC).date()

        if "сегодня" in date_text:
            return today
        if "вчера" in date_text:
            return today - timedelta(days=1)

        months = {
            "январ": 1,
            "феврал": 2,
            "март": 3,
            "апрел": 4,
            "мая": 5,
            "май": 5,
            "июн": 6,
            "июл": 7,
            "август": 8,
            "сентябр": 9,
            "октябр": 10,
            "ноябр": 11,
            "декабр": 12,
        }

        day_match = re.search(r"(\d{1,2})", date_text)
        if not day_match:
            return today

        day = int(day_match.group(1))
        month = today.month
        year = today.year

        for month_name, month_num in months.items():
            if month_name in date_text:
                month = month_num
                break

        year_match = re.search(r"(\d{4})", date_text)
        if year_match:
            year = int(year_match.group(1))

        try:
            return date(year, month, day)
        except ValueError:
            return today

    def _scan_page_dates(self, tree: HTMLParser) -> dict[str, date]:
        result: dict[str, date] = {}

        for article in tree.css("article"):
            link = article.css_first("a.vac-small__title-link")
            if not link:
                continue

            href = link.attributes.get("href", "")
            match = re.search(r"/vacancy/(\d+)/", href or "")

            if not match:
                continue

            vacancy_id = match.group(1)

            date_node = article.css_first("div.vac-small__upped-time")
            if not date_node:
                continue

            vacancy_date = self._parse_relative_date(date_node.text(strip=True))
            result[vacancy_id] = vacancy_date

        return result

    async def stream_vacancies(
        self,
        client: httpx.AsyncClient,
        target_date: date,
    ) -> AsyncGenerator[list[ParserVacancyResult], None]:
        page = 1
        seen_ids: set[str] = set()
        found_target_date = False
        consecutive_empty = 0
        max_consecutive_empty = 100
        max_pages = praca_config.PRACA_MAX_PAGES

        while page <= max_pages:
            url = f"{praca_config.PRACA_SEARCH_URL}?page={page}&sort-field=time"
            html = await self._request(client, url)

            if not html:
                break

            tree = HTMLParser(html)
            page_dates = self._scan_page_dates(tree)

            if not page_dates:
                break

            target_ids = [
                vid
                for vid, vdate in page_dates.items()
                if vdate == target_date and vid not in seen_ids
            ]

            if target_ids:
                found_target_date = True
                consecutive_empty = 0

                page_vacancies: list[ParserVacancyResult] = []

                for vacancy_id in target_ids:
                    seen_ids.add(vacancy_id)
                    vacancy = await self.fetch_vacancy_details(client, vacancy_id)
                    if vacancy:
                        page_vacancies.append(vacancy)

                if page_vacancies:
                    logger.info(
                        "PracaBy page %s: %s vacancies for %s (total: %s)",
                        page,
                        len(page_vacancies),
                        target_date,
                        len(seen_ids),
                    )
                    yield page_vacancies
            else:
                if found_target_date:
                    consecutive_empty += 1

            if found_target_date and consecutive_empty >= max_consecutive_empty:
                logger.info(
                    "PracaBy: %s empty pages after last find, stopping at page %s",
                    consecutive_empty,
                    page,
                )
                break

            page += 1

        logger.info(
            "PracaBy: finished at page %s, found %s vacancies for %s",
            page,
            len(seen_ids),
            target_date,
        )

    async def fetch_vacancy_details(
        self,
        client: httpx.AsyncClient,
        vacancy_id: str,
    ) -> ParserVacancyResult | None:
        url = f"{praca_config.PRACA_BASE_URL}/vacancy/{vacancy_id}/"
        html = await self._request(client, url)

        if not html:
            return None

        try:
            return self._parse_vacancy_page(html, vacancy_id, url)
        except Exception as e:
            logger.error("Failed to parse vacancy %s: %s", vacancy_id, e)
            return None

    def _parse_vacancy_page(
        self,
        html: str,
        vacancy_id: str,
        url: str,
    ) -> ParserVacancyResult:
        tree = HTMLParser(html)

        title_node = tree.css_first("h1")
        title = title_node.text(strip=True) if title_node else "Без названия"

        salary_from, salary_to, currency = self._parse_salary(tree)

        company_node = tree.css_first("div.vacancy__org-name a")
        company_name = company_node.text(strip=True) if company_node else None

        company_external_id = None
        if company_node:
            href = company_node.attributes.get("href", "")
            match = re.search(r"/organization/(\d+)/", href or "")

            if match:
                company_external_id = match.group(1)

        city_node = tree.css_first("div.vacancy__city")
        city = city_node.text(strip=True) if city_node else None

        address_node = tree.css_first("div.job-address")
        address = address_node.text(strip=True) if address_node else None

        description_node = tree.css_first("div.vacancy__description div.description")
        description = description_node.html if description_node else None

        experience_node = tree.css_first("p.vacancy__experience")
        experience = experience_node.text(strip=True) if experience_node else None

        education_node = tree.css_first("p.vacancy__education")
        education = education_node.text(strip=True) if education_node else None

        schedule = None
        employment = None
        is_remote = False
        internship = False

        for item in tree.css("div.vacancy-required__first-block div.vacancy__item"):
            text = item.text(strip=True)

            if "График работы:" in text:
                schedule = text.replace("График работы:", "").strip()
            elif "Занятость:" in text:
                employment = text.replace("Занятость:", "").strip()
                if "стажировка" in employment.lower():
                    internship = True
            elif "Характер работы:" in text:
                work_type = text.replace("Характер работы:", "").strip()
                is_remote = "удалённ" in work_type.lower() or "дистанционн" in work_type.lower()

        published_at = None
        date_node = tree.css_first("div.vacancy__common-info time")
        if date_node:
            datetime_attr = date_node.attributes.get("datetime")
            if datetime_attr:
                try:
                    published_at = datetime.fromisoformat(datetime_attr)
                except ValueError:
                    pass

        return ParserVacancyResult(
            external_id=vacancy_id,
            title=title,
            description=description,
            company_name=company_name,
            company_external_id=company_external_id,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            city=city,
            address=address,
            experience=experience,
            education=education,
            employment=employment,
            schedule=schedule,
            is_remote=is_remote,
            published_at=published_at,
            internship=internship,
            created_at=None,
            vacancy_url=url,
        )

    def _parse_salary(self, tree: HTMLParser) -> tuple[int | None, int | None, str | None]:
        salary_node = tree.css_first("div.vacancy__salary")
        if not salary_node:
            return None, None, None

        salary_text = salary_node.text(strip=True)
        clean_text = re.sub(r"(\d)\s+(\d)", r"\1\2", salary_text)
        numbers = re.findall(r"(\d+)", clean_text)

        salary_from = None
        salary_to = None
        currency = "BYN"

        if "$" in salary_text or "usd" in salary_text.lower():
            currency = "USD"
        elif "€" in salary_text or "eur" in salary_text.lower():
            currency = "EUR"

        if len(numbers) >= 2:
            salary_from = int(numbers[0])
            salary_to = int(numbers[1])
        elif len(numbers) == 1:
            if "от" in salary_text.lower():
                salary_from = int(numbers[0])
            elif "до" in salary_text.lower():
                salary_to = int(numbers[0])
            else:
                salary_from = int(numbers[0])

        return salary_from, salary_to, currency
