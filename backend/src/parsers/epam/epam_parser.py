import asyncio
import re
from collections.abc import AsyncGenerator
from random import uniform
from typing import Any

from fastapi import status
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
)
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import (
    async_playwright,
)
from selectolax.parser import HTMLParser

from src.core.config import epam_config
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult


class EpamParser:
    def __init__(self, max_concurrent: int = 5) -> None:
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright: Playwright | None = None
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def _ensure_browser(self) -> BrowserContext:
        if self._browser is None or self._context is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
        return self._context

    async def close(self) -> None:
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def _create_page(self) -> Page:
        context = await self._ensure_browser()
        return await context.new_page()

    async def _fetch_page_with_js(
        self,
        url: str,
        wait_selector: str,
        timeout: int = 30000,
    ) -> str | None:
        page = await self._create_page()

        try:
            for attempt in range(epam_config.EPAM_RETRIES):
                try:
                    await asyncio.sleep(epam_config.EPAM_RATE_LIMIT_DELAY + uniform(0.1, 0.2))
                    await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                    await page.wait_for_selector(wait_selector, timeout=timeout)
                    return await page.content()

                except PlaywrightTimeout:
                    logger.warning("EPAM timeout (attempt %s) for %s", attempt + 1, url)
                except Exception as e:
                    logger.warning("EPAM error (attempt %s): %s", attempt + 1, e)

                if attempt < epam_config.EPAM_RETRIES - 1:
                    await asyncio.sleep(2 * (attempt + 1))

            return None
        finally:
            await page.close()

    async def _fetch_static_page(self, url: str, timeout: int = 20000) -> str | None:
        async with self._semaphore:
            page = await self._create_page()

            try:
                for attempt in range(epam_config.EPAM_RETRIES):
                    try:
                        await asyncio.sleep(epam_config.EPAM_RATE_LIMIT_DELAY + uniform(0.1, 0.3))

                        response = await page.goto(
                            url, wait_until="domcontentloaded", timeout=timeout
                        )

                        if response and response.status == status.HTTP_200_OK:
                            try:
                                await page.wait_for_selector(
                                    "[data-testid='job-details-banner-title'], h1",
                                    timeout=5000,
                                )
                            except PlaywrightTimeout:
                                pass

                            return await page.content()

                        if response and response.status == status.HTTP_429_TOO_MANY_REQUESTS:
                            wait_time = 30 * (attempt + 1)
                            logger.warning("EPAM 429! Backoff %ss", wait_time)
                            await asyncio.sleep(wait_time)
                            continue

                        logger.warning(
                            "EPAM bad status %s for %s",
                            response.status if response else "None",
                            url,
                        )

                    except PlaywrightTimeout:
                        logger.warning("EPAM timeout (attempt %s) for %s", attempt + 1, url)
                    except Exception as e:
                        logger.warning("EPAM error (attempt %s): %s", attempt + 1, e)

                    if attempt < epam_config.EPAM_RETRIES - 1:
                        await asyncio.sleep(1 * (attempt + 1))

                return None
            finally:
                await page.close()

    def _extract_vacancy_ids_from_list(self, html: str) -> list[dict[str, str]]:
        tree = HTMLParser(html)
        vacancies: list[dict[str, str]] = []

        for card in tree.css("[data-testid='job-card-link']"):
            href = card.attributes.get("href", "")
            if not href:
                continue

            match = re.search(r"/vacancy/([^/]+)", href)
            if match:
                vacancy_slug = match.group(1)
                external_id = self._extract_external_id(vacancy_slug)
                vacancies.append(
                    {
                        "external_id": external_id,
                        "slug": vacancy_slug,
                        "url": f"{epam_config.EPAM_BASE_URL}{href}",
                    }
                )

        return vacancies

    def _extract_external_id(self, slug: str) -> str:
        match = re.search(r"(blt[a-z0-9]+)", slug, re.IGNORECASE)
        if match:
            return match.group(1)
        return slug

    def _has_next_page(self, html: str) -> bool:
        tree = HTMLParser(html)

        next_button = tree.css_first("button[aria-label='next page']")
        if not next_button:
            return False

        if "disabled" in next_button.attributes:
            return False

        return True

    async def _fetch_vacancy_details(
        self,
        url: str,
        external_id: str,
    ) -> ParserVacancyResult | None:
        html = await self._fetch_static_page(url)

        if not html:
            logger.warning("EPAM: failed to fetch vacancy %s", external_id)
            return None

        try:
            return self._parse_vacancy_page(html, external_id, url)
        except Exception as e:
            logger.error("EPAM: failed to parse vacancy %s: %s", external_id, e)
            return None

    async def _fetch_vacancies_batch(
        self,
        refs: list[dict[str, str]],
    ) -> list[ParserVacancyResult]:
        tasks = [self._fetch_vacancy_details(ref["url"], ref["external_id"]) for ref in refs]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        vacancies = []
        for result in results:
            if isinstance(result, ParserVacancyResult):
                vacancies.append(result)
            elif isinstance(result, Exception):
                logger.error("EPAM: batch fetch error: %s", result)

        return vacancies

    async def stream_vacancies(self) -> AsyncGenerator[list[ParserVacancyResult], None]:
        page = 1
        seen_ids: set[str] = set()

        try:
            while page <= epam_config.EPAM_MAX_PAGES:
                url = f"{epam_config.EPAM_SEARCH_URL}?country=&page={page}&sort_by=relevance"

                html = await self._fetch_page_with_js(
                    url,
                    wait_selector="[data-testid='job-card-link']",
                )

                if not html:
                    logger.error("EPAM: failed to fetch page %s", page)
                    break

                vacancy_refs = self._extract_vacancy_ids_from_list(html)

                if not vacancy_refs:
                    logger.info("EPAM: no vacancies found on page %s, stopping", page)
                    break

                duplicates = [ref for ref in vacancy_refs if ref["external_id"] in seen_ids]

                new_refs = [ref for ref in vacancy_refs if ref["external_id"] not in seen_ids]

                if duplicates:
                    duplicate_ids = [ref["external_id"] for ref in duplicates]
                    logger.warning(
                        "EPAM page %s: found %s duplicates: %s",
                        page,
                        len(duplicates),
                        duplicate_ids,
                    )
                    for ref in duplicates:
                        logger.warning("  - %s: %s", ref["external_id"], ref["url"])

                if not new_refs:
                    logger.info("EPAM: all vacancies on page %s already seen, stopping", page)
                    break

                for ref in new_refs:
                    seen_ids.add(ref["external_id"])

                page_vacancies = await self._fetch_vacancies_batch(new_refs)

                failed_count = len(new_refs) - len(page_vacancies)
                if failed_count > 0:
                    logger.warning(
                        "EPAM page %s: failed to fetch %s vacancies",
                        page,
                        failed_count,
                    )

                if page_vacancies:
                    logger.info(
                        "EPAM page %s: %s vacancies (total seen: %s)",
                        page,
                        len(page_vacancies),
                        len(seen_ids),
                    )
                    yield page_vacancies

                if not self._has_next_page(html):
                    logger.info("EPAM: reached last page %s", page)
                    break

                page += 1

            logger.info("EPAM: finished at page %s, total %s vacancies", page, len(seen_ids))

        finally:
            await self.close()

    def _parse_vacancy_page(
        self,
        html: str,
        external_id: str,
        url: str,
    ) -> ParserVacancyResult:
        tree = HTMLParser(html)

        title = self._extract_title(tree)
        description = self._extract_description(tree)
        location_info = self._extract_location(tree)
        skills = self._extract_skills(tree, location_info["countries"])
        experience = self._extract_experience(tree)
        responsibilities = self._extract_section(tree, "Responsibilities")
        requirements = self._extract_section(tree, "Requirements")
        nice_to_have = self._extract_section(tree, "Nice to have")
        benefits = self._extract_section(tree, "We offer/Benefits")

        full_description = self._build_full_description(
            description,
            responsibilities,
            requirements,
            nice_to_have,
            benefits,
        )

        return ParserVacancyResult(
            external_id=external_id,
            title=title,
            description=full_description,
            company_name="EPAM Systems",
            company_external_id="epam",
            salary_from=None,
            salary_to=None,
            currency=None,
            city=None,
            address=location_info["address"],
            experience=experience,
            education=None,
            employment=None,
            schedule=None,
            is_remote=location_info["is_remote"],
            published_at=None,
            internship=self._is_internship(title, full_description),
            created_at=None,
            vacancy_url=url,
            skills=skills,
        )

    def _extract_title(self, tree: HTMLParser) -> str:
        title_node = tree.css_first("[data-testid='job-details-banner-title']")
        if title_node:
            return title_node.text(strip=True)

        h1_node = tree.css_first("h1")
        if h1_node:
            return h1_node.text(strip=True)

        return "Unknown Position"

    def _extract_description(self, tree: HTMLParser) -> str | None:
        desc_node = tree.css_first("[data-testid='description-content']")
        if desc_node:
            rich_text = desc_node.css_first("[data-testid='rich-text']")
            if rich_text:
                return rich_text.html
        return None

    def _extract_location(self, tree: HTMLParser) -> dict[str, Any]:
        result: dict[str, Any] = {
            "address": None,
            "is_remote": False,
            "countries": set(),
        }

        upper_bar = tree.css_first("[data-testid='upper-bar']")
        if not upper_bar:
            return result

        icon_bullets = upper_bar.css("[data-testid='icon-bullet-container']")

        for bullet in icon_bullets:
            text = bullet.text(strip=True)

            if "Remote" in text:
                result["is_remote"] = True

            for link in bullet.css("[data-testid='icon-bullet-link-item-link']"):
                href = link.attributes.get("href", "") or ""
                match = re.search(r"/en/([a-z-]+)-it-jobs", href)
                if match:
                    country_slug = match.group(1)
                    country_name = country_slug.replace("-", " ").title()
                    result["countries"].add(country_name)

        if result["countries"]:
            result["address"] = ", ".join(sorted(result["countries"]))

        return result

    def _extract_skills(self, tree: HTMLParser, countries: set[str]) -> list[str]:
        skills: list[str] = []
        countries_lower = {c.lower() for c in countries}

        upper_bar = tree.css_first("[data-testid='upper-bar']")
        if upper_bar:
            for bullet in upper_bar.css("[data-testid='icon-bullet-container']"):
                for item in bullet.css("[data-testid='icon-bullet-item']"):
                    text = item.text(strip=True)
                    if (
                        text
                        and "Remote" not in text
                        and "Hybrid" not in text
                        and "Office" not in text
                        and text.lower() not in countries_lower
                    ):
                        skills.append(text)

        return skills

    def _extract_experience(self, tree: HTMLParser) -> str | None:
        requirements_section = self._extract_section(tree, "Requirements")
        if not requirements_section:
            return None

        experience_patterns = [
            r"(\d+\+?\s*years?\s+(?:of\s+)?experience)",
            r"(\d+\+?\s*years?\s+in\s+\w+)",
            r"(at\s+least\s+\d+\s+years?)",
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, requirements_section, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_section(self, tree: HTMLParser, section_name: str) -> str | None:
        for accordion in tree.css("[data-testid='accordion-section-container']"):
            label = accordion.css_first("[data-testid='accordion-section-label-container']")
            if label and section_name.lower() in label.text(strip=True).lower():
                content = accordion.css_first(
                    "[data-testid='accordion-section-children-container']"
                )
                if content:
                    return content.html
        return None

    def _build_full_description(
        self,
        description: str | None,
        responsibilities: str | None,
        requirements: str | None,
        nice_to_have: str | None,
        benefits: str | None,
    ) -> str:
        parts: list[str] = []

        if description:
            parts.append(description)
        if responsibilities:
            parts.append(f"<h3>Responsibilities</h3>{responsibilities}")
        if requirements:
            parts.append(f"<h3>Requirements</h3>{requirements}")
        if nice_to_have:
            parts.append(f"<h3>Nice to have</h3>{nice_to_have}")
        if benefits:
            parts.append(f"<h3>Benefits</h3>{benefits}")

        return "\n".join(parts) if parts else ""

    def _is_internship(self, title: str, description: str | None) -> bool:
        internship_keywords = ["intern", "internship", "trainee", "стажер", "стажировка"]
        combined = f"{title} {description or ''}".lower()
        return any(keyword in combined for keyword in internship_keywords)
