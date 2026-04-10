import asyncio
import re
from collections.abc import AsyncGenerator
from random import uniform

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

from src.core.config import wargaming_config
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult


class WargamingParser:
    def __init__(self) -> None:
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright: Playwright | None = None
        self._semaphore = asyncio.Semaphore(wargaming_config.WARGAMING_MAX_CONCURRENT)

    async def _ensure_browser(self) -> BrowserContext:
        if self._browser is None or self._context is None:
            self._playwright = await async_playwright().start()

            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-setuid-sandbox",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--mute-audio",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-component-update",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-features=TranslateUI",
                    "--disable-hang-monitor",
                    "--disable-ipc-flooding-protection",
                    "--disable-popup-blocking",
                    "--disable-prompt-on-repost",
                    "--disable-renderer-backgrounding",
                    "--disable-sync",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                ],
            )

            self._context = await self._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="Europe/Berlin",
                geolocation={"latitude": 52.52, "longitude": 13.405},
                permissions=["geolocation"],
                color_scheme="light",
                java_script_enabled=True,
                has_touch=False,
                is_mobile=False,
                device_scale_factor=1,
            )

            await self._context.add_init_script(
                """
                // Перезаписываем navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                // Перезаписываем plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                // Перезаписываем languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                // Скрываем chrome
                window.chrome = {
                    runtime: {},
                };
                // Перезаписываем permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """
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

    async def _load_all_vacancies(self, page: Page) -> str:
        logger.info("Wargaming: navigating to careers page...")

        await page.goto(
            wargaming_config.WARGAMING_CAREERS_URL,
            wait_until="domcontentloaded",
            timeout=wargaming_config.WARGAMING_TIMEOUT * 1000,
        )

        try:
            await page.wait_for_selector("section.jobs", timeout=15000)
            logger.info("Wargaming: found section.jobs")
        except PlaywrightTimeout:
            try:
                await page.wait_for_selector("a.title", timeout=10000)
                logger.info("Wargaming: found a.title")
            except PlaywrightTimeout:
                logger.error("Wargaming: could not find job list elements")
                return await page.content()

        await asyncio.sleep(1.5)

        last_count = 0
        stale_count = 0

        while True:
            show_more = await page.query_selector("div.show-more a")

            if not show_more or not await show_more.is_visible():
                logger.info("Wargaming: 'Show more' button not found or hidden, all loaded")
                break

            current_items = await page.query_selector_all("a.title")
            current_count = len(current_items)

            if current_count == last_count:
                stale_count += 1
                if stale_count >= 3:
                    logger.info(
                        "Wargaming: no new vacancies after %s attempts, stopping", stale_count
                    )
                    break
            else:
                stale_count = 0
                last_count = current_count

            try:
                await show_more.click()
                await asyncio.sleep(1.0 + uniform(1.0, 2.0))
                logger.debug("Wargaming: loaded %s vacancies so far", current_count)

            except Exception as e:
                logger.warning("Wargaming: error clicking 'Show more': %s", e)
                stale_count += 1
                if stale_count >= 3:
                    break

        final_items = await page.query_selector_all("a.title")
        logger.info("Wargaming: finished loading, total %s vacancy links", len(final_items))

        return await page.content()

    def _extract_vacancy_refs(self, html: str) -> list[dict[str, str]]:
        tree = HTMLParser(html)
        vacancies = []

        for item in tree.css("ul.job-list li li"):
            link = item.css_first("a.title")
            if not link:
                continue

            href = link.attributes.get("href", "")
            if not href or "/vacancy_" not in href:
                continue

            match = re.search(r"/(vacancy_\d+_[^/]+)/?$", href)
            if not match:
                continue

            external_id = match.group(1)
            title = link.text(strip=True)

            desc_node = item.css_first("div.description")
            department = desc_node.text(strip=True) if desc_node else "No info"

            place_node = item.css_first("div.place")
            location = place_node.text(strip=True) if place_node else "No info"

            vacancies.append(
                {
                    "external_id": external_id,
                    "url": f"{wargaming_config.WARGAMING_BASE_URL}{href}",
                    "title": title,
                    "department": department,
                    "location": location,
                }
            )

        return vacancies

    async def _fetch_vacancy_details(
        self,
        url: str,
        external_id: str,
        prefetched_data: dict[str, str],
    ) -> ParserVacancyResult | None:
        async with self._semaphore:
            page = await self._create_page()

            try:
                for attempt in range(wargaming_config.WARGAMING_RETRIES):
                    try:
                        await asyncio.sleep(
                            wargaming_config.WARGAMING_RATE_LIMIT_DELAY + uniform(1.0, 1.5)
                        )

                        response = await page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=wargaming_config.WARGAMING_TIMEOUT * 1000,
                        )

                        if response and response.status == 200:
                            try:
                                await page.wait_for_selector(
                                    "section.vacancy",
                                    timeout=10000,
                                )
                            except PlaywrightTimeout:
                                pass

                            html = await page.content()
                            return self._parse_vacancy_page(html, external_id, url, prefetched_data)

                        logger.warning(
                            "Wargaming: bad status %s for %s",
                            response.status if response else "None",
                            url,
                        )

                    except PlaywrightTimeout:
                        logger.warning(
                            "Wargaming: timeout (attempt %s) for %s",
                            attempt + 1,
                            url,
                        )
                    except Exception as e:
                        logger.warning(
                            "Wargaming: error (attempt %s): %s",
                            attempt + 1,
                            e,
                        )

                    if attempt < wargaming_config.WARGAMING_RETRIES - 1:
                        await asyncio.sleep(2 * (attempt + 1))

                logger.error(
                    "Wargaming: FAILED to fetch vacancy %s after %s retries: %s",
                    external_id,
                    wargaming_config.WARGAMING_RETRIES,
                    url,
                )
                return None

            finally:
                await page.close()

    def _clean_description(self, html: str | None) -> str | None:
        if not html:
            return None

        tree = HTMLParser(html)

        for img in tree.css("img"):
            img.decompose()

        for iframe in tree.css("iframe"):
            iframe.decompose()

        full_text = tree.html or ""

        full_text = re.sub(
            r"<h3[^>]*>\s*<strong>\s*Reports\s+to\s*</strong>\s*</h3>.*?(?=<h3[^>]*>\s*<strong>\s*What\s+will\s+you\s+do)",
            "",
            full_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        full_text = re.sub(
            r"<h5[^>]*>\s*Please\s+submit\s+your\s+CV.*$",
            "",
            full_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        full_text = re.sub(
            r'<div[^>]*class="content-conclusion"[^>]*>.*?</div>',
            "",
            full_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        full_text = re.sub(
            r"<h3[^>]*>\s*<strong>\s*<img[^>]*>\s*</strong>\s*</h3>",
            "",
            full_text,
            flags=re.IGNORECASE,
        )

        full_text = re.sub(r"<h3[^>]*>\s*(&nbsp;|\s)*\s*</h3>", "", full_text)

        full_text = re.sub(r"\n\s*\n", "\n", full_text)
        full_text = full_text.strip()

        return full_text if full_text else None

    def _parse_vacancy_page(
        self,
        html: str,
        external_id: str,
        url: str,
        prefetched_data: dict[str, str],
    ) -> ParserVacancyResult:
        tree = HTMLParser(html)

        title_node = tree.css_first("section.vacancy h1")
        title = (
            title_node.text(strip=True)
            if title_node
            else prefetched_data.get("title", "Unknown Position")
        )

        place_node = tree.css_first("section.vacancy div.place")
        location = place_node.text(strip=True) if place_node else prefetched_data.get("location")

        city = None
        if location:
            parts = location.split(",")
            if parts:
                city = parts[0].strip()

        dept_node = tree.css_first("section.vacancy div.col-2 div.title")
        department = dept_node.text(strip=True) if dept_node else prefetched_data.get("department")

        desc_node = tree.css_first("section.vacancy div.list._intro")
        raw_description = desc_node.html if desc_node else None

        description = self._clean_description(raw_description)

        is_remote = False
        if description:
            desc_lower = description.lower()
            is_remote = "remote" in desc_lower or "hybrid" in desc_lower

        experience = self._extract_experience(description)

        internship = False
        if title:
            title_lower = title.lower()
            internship = any(kw in title_lower for kw in ["intern", "internship", "trainee"])

        return ParserVacancyResult(
            external_id=external_id,
            title=title,
            description=description,
            company_name="Wargaming",
            company_external_id="wargaming",
            salary_from=None,
            salary_to=None,
            currency=None,
            city=city,
            address=location,
            experience=experience,
            education=None,
            employment=department,
            schedule=None,
            is_remote=is_remote,
            published_at=None,
            internship=internship,
            created_at=None,
            vacancy_url=url,
            skills=[],
        )

    def _extract_experience(self, description: str | None) -> str | None:
        if not description:
            return None

        patterns = [
            r"(\d+\+?\s*years?\s+(?:of\s+)?experience)",
            r"(\d+\+?\s*years?\s+in\s+\w+)",
            r"(at\s+least\s+\d+\s+years?)",
            r"(\d+\+?\s*years?\s+of\s+\w+\s+experience)",
        ]

        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    async def _fetch_vacancies_batch(
        self,
        refs: list[dict[str, str]],
    ) -> list[ParserVacancyResult]:
        tasks = [
            self._fetch_vacancy_details(
                ref["url"],
                ref["external_id"],
                ref,
            )
            for ref in refs
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        vacancies: list[ParserVacancyResult] = []
        for result in results:
            if isinstance(result, ParserVacancyResult):
                vacancies.append(result)
            elif isinstance(result, Exception):
                logger.error("Wargaming: batch fetch error: %s", result)

        return vacancies

    async def stream_vacancies(self) -> AsyncGenerator[list[ParserVacancyResult], None]:
        page = await self._create_page()

        try:
            logger.info("Wargaming: loading all vacancy links...")
            html = await self._load_all_vacancies(page)
            await page.close()

            vacancy_refs = self._extract_vacancy_refs(html)
            logger.info(
                "Wargaming: found %s vacancy links, fetching details...",
                len(vacancy_refs),
            )

            if not vacancy_refs:
                logger.warning("Wargaming: no vacancies found")
                return

            batch_size = wargaming_config.WARGAMING_BATCH_SIZE

            for i in range(0, len(vacancy_refs), batch_size):
                batch_refs = vacancy_refs[i : i + batch_size]

                batch_vacancies = await self._fetch_vacancies_batch(batch_refs)

                if batch_vacancies:
                    logger.info(
                        "Wargaming: batch %s-%s: %s vacancies (total refs: %s)",
                        i + 1,
                        min(i + batch_size, len(vacancy_refs)),
                        len(batch_vacancies),
                        len(vacancy_refs),
                    )
                    yield batch_vacancies

        finally:
            await self.close()
