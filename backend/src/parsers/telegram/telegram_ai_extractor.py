import json
from typing import Any

from src.ai.groq_client import GroqClient
from src.ai.prompts import VACANCY_EXTRACTION_PROMPT
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.telegram.schemas import ExtractionResult, TelegramMessage


class TelegramAIExtractor:
    def __init__(self) -> None:
        self._client: GroqClient | None = None

    async def connect(self) -> None:
        self._client = GroqClient()
        await self._client.__aenter__()
        logger.info("AI extractor connected")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
            logger.info("AI extractor disconnected")

    def _ensure_client(self) -> GroqClient:
        if self._client is None:
            raise RuntimeError("AI client not connected")
        return self._client

    async def extract_vacancy(self, message: TelegramMessage) -> ExtractionResult:
        client = self._ensure_client()

        try:
            response = await client.chat(
                content=message.text,
                system_prompt=VACANCY_EXTRACTION_PROMPT,
            )

            vacancy = self._parse_ai_response(
                response.content,
                message,
            )

            return ExtractionResult(
                vacancy=vacancy,
                raw_response=response.content,
                success=vacancy is not None,
            )

        except Exception as e:
            logger.error(
                "AI extraction failed for message %d: %s",
                message.id,
                e,
            )
            return ExtractionResult(
                vacancy=None,
                raw_response="",
                success=False,
                error=str(e),
            )

    def _parse_ai_response(
        self,
        content: str,
        message: TelegramMessage,
    ) -> ParserVacancyResult | None:
        try:
            data = self._extract_json(content)

            title = data.get("title")
            if not title:
                logger.warning(
                    "AI response missing title for message %d",
                    message.id,
                )
                return None

            external_id = data.get("external_id")
            if not external_id:
                external_id = f"tg_{message.channel.lstrip('@')}_{message.id}"

            return ParserVacancyResult(
                external_id=str(external_id),
                vacancy_url=message.url,
                title=title,
                description=data.get("description"),
                company_name=data.get("company_name"),
                company_external_id=data.get("company_external_id"),
                salary_from=self._safe_int(data.get("salary_from")),
                salary_to=self._safe_int(data.get("salary_to")),
                currency=data.get("currency"),
                city=data.get("city"),
                address=data.get("address"),
                is_remote=bool(data.get("is_remote", False)),
                experience=data.get("experience"),
                education=data.get("education"),
                employment=data.get("employment"),
                schedule=data.get("schedule"),
                internship=data.get("internship"),
                skills=data.get("skills") or [],
                published_at=message.date,
                created_at=message.date,
            )

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse AI JSON for message %d: %s\nContent: %s",
                message.id,
                e,
                content[:500],
            )
            return None

    @staticmethod
    def _extract_json(content: str) -> dict:
        content = content.strip()

        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline != -1:
                content = content[first_newline + 1 :]
            else:
                content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
