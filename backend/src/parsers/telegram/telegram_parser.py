from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import UTC, datetime
from types import TracebackType

from telethon import TelegramClient
from telethon.tl.types import Message

from src.core.config import telegram_config
from src.core.logger import logger


@dataclass
class TelegramMessage:
    id: int
    text: str
    date: datetime
    channel: str
    url: str


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class TelegramParser:
    def __init__(self) -> None:
        self._client: TelegramClient | None = None

    async def connect(self) -> None:
        self._client = TelegramClient(
            telegram_config.TELEGRAM_SESSION_NAME,
            telegram_config.TELEGRAM_API_ID,
            telegram_config.TELEGRAM_API_HASH,
        )
        await self._client.start(phone=telegram_config.TELEGRAM_PHONE)
        logger.info("Telegram client connected")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None
            logger.info("Telegram client disconnected")

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

    async def stream_messages(
        self,
        channel: str,
        from_date: datetime,
        to_date: datetime,
    ) -> AsyncGenerator[list[TelegramMessage], None]:
        client = self._ensure_client()

        from_date = _ensure_utc(from_date)
        to_date = _ensure_utc(to_date)

        batch: list[TelegramMessage] = []
        batch_size = 50

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

            batch.append(
                TelegramMessage(
                    id=message.id,
                    text=message.text,
                    date=msg_date,
                    channel=channel,
                    url=f"https://t.me/{channel_username}/{message.id}",
                )
            )

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

        logger.info(
            "Telegram %s: finished streaming %s to %s",
            channel,
            from_date.date(),
            to_date.date(),
        )
