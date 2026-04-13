import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from types import TracebackType

from telethon import TelegramClient
from telethon.tl.types import Message

from src.core.config import telegram_config
from src.core.logger import logger
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.telegram.schemas import TelegramMessage
from src.parsers.telegram.telegram_ai_extractor import TelegramAIExtractor


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class TelegramParser:
    BATCH_SIZE: int = 10
    AI_DELAY: float = 2

    def __init__(self) -> None:
        self._client: TelegramClient | None = None
        self._extractor: TelegramAIExtractor | None = None

    async def connect(self) -> None:
        self._client = TelegramClient(
            telegram_config.TELEGRAM_SESSION_NAME,
            telegram_config.TELEGRAM_API_ID,
            telegram_config.TELEGRAM_API_HASH,
        )
        await self._client.start(phone=telegram_config.TELEGRAM_PHONE)

        self._extractor = TelegramAIExtractor()
        await self._extractor.connect()

        logger.info("Telegram parser connected")

    async def disconnect(self) -> None:
        if self._extractor:
            await self._extractor.disconnect()
            self._extractor = None

        if self._client:
            await self._client.disconnect()
            self._client = None

        logger.info("Telegram parser disconnected")

    async def __aenter__(self) -> "TelegramParser":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.disconnect()

    def _ensure_client(self) -> TelegramClient:
        if self._client is None:
            raise RuntimeError("Telegram client not connected")
        return self._client

    def _ensure_extractor(self) -> TelegramAIExtractor:
        if self._extractor is None:
            raise RuntimeError("AI extractor not initialized")
        return self._extractor

    async def _iter_messages(
        self,
        channel: str,
        from_date: datetime,
        to_date: datetime,
    ) -> AsyncGenerator[TelegramMessage, None]:
        client = self._ensure_client()

        from_date = _ensure_utc(from_date)
        to_date = _ensure_utc(to_date)

        async for message in client.iter_messages(
            channel,
            offset_date=to_date,
            reverse=False,
        ):
            if not isinstance(message, Message):
                continue

            if not message.text:
                continue

            msg_date = message.date

            if msg_date < from_date:
                break

            if msg_date > to_date:
                continue

            channel_username = channel.lstrip("@")

            yield TelegramMessage(
                id=message.id,
                text=message.text,
                date=msg_date,
                channel=channel,
                url=f"https://t.me/{channel_username}/{message.id}",
            )

    async def stream_vacancies(
        self,
        channel: str,
        from_date: datetime,
        to_date: datetime,
    ) -> AsyncGenerator[list[ParserVacancyResult], None]:
        extractor = self._ensure_extractor()
        batch: list[ParserVacancyResult] = []

        async for msg in self._iter_messages(channel, from_date, to_date):
            result = await extractor.extract_vacancy(msg)

            if result.success and result.vacancy:
                batch.append(result.vacancy)

                logger.info(
                    "Message %d → %s (%s)",
                    msg.id,
                    result.vacancy.title,
                    result.vacancy.company_name or "?",
                )
            else:
                logger.debug(
                    "Message %d skipped: %s",
                    msg.id,
                    result.error or "not a vacancy",
                )

            await asyncio.sleep(self.AI_DELAY)

            if len(batch) >= self.BATCH_SIZE:
                yield batch
                batch = []

        if batch:
            yield batch

        logger.info(
            "Telegram %s: finished %s to %s",
            channel,
            from_date.date(),
            to_date.date(),
        )
