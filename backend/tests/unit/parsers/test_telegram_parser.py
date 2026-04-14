from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.telegram.schemas import TelegramMessage
from src.parsers.telegram.telegram_ai_extractor import ExtractionResult
from src.parsers.telegram.telegram_parser import TelegramParser, _ensure_utc


@pytest.fixture
def parser() -> TelegramParser:
    return TelegramParser()


@pytest.fixture
def sample_message() -> TelegramMessage:
    return TelegramMessage(
        id=12345,
        text="Looking for Python Developer\nCompany: TechCorp\nSalary: $3000-5000",
        date=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
        channel="@jobchannel",
        url="https://t.me/jobchannel/12345",
    )


@pytest.fixture
def sample_vacancy() -> ParserVacancyResult:
    return ParserVacancyResult(
        external_id="tg_12345",
        title="Python Developer",
        company_name="TechCorp",
        salary_from=3000,
        salary_to=5000,
        currency="USD",
        is_remote=True,
        vacancy_url="https://t.me/jobchannel/12345",
    )


@pytest.fixture
def sample_extraction_result(sample_vacancy: ParserVacancyResult) -> ExtractionResult:
    return ExtractionResult(
        success=True,
        vacancy=sample_vacancy,
        error=None,
        raw_response="{}",
    )


@pytest.fixture
def failed_extraction_result() -> ExtractionResult:
    return ExtractionResult(
        success=False,
        vacancy=None,
        error="Not a vacancy",
        raw_response="{}",
    )


class TestEnsureUtc:
    def test_adds_utc_to_naive_datetime(self) -> None:
        naive = datetime(2024, 6, 15, 10, 0, 0)
        result = _ensure_utc(naive)

        assert result.tzinfo == UTC
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_converts_aware_datetime_to_utc(self) -> None:
        from datetime import timezone

        other_tz = timezone(timedelta(hours=3))
        aware = datetime(2024, 6, 15, 13, 0, 0, tzinfo=other_tz)

        result = _ensure_utc(aware)

        assert result.tzinfo == UTC
        assert result.hour == 10

    def test_keeps_utc_datetime_unchanged(self) -> None:
        utc_dt = datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC)
        result = _ensure_utc(utc_dt)

        assert result == utc_dt
        assert result.tzinfo == UTC


class TestConnect:
    @pytest.mark.asyncio
    async def test_connects_client_and_extractor(self, parser: TelegramParser) -> None:
        mock_client = AsyncMock()
        mock_extractor = AsyncMock()

        with (
            patch(
                "src.parsers.telegram.telegram_parser.TelegramClient",
                return_value=mock_client,
            ),
            patch(
                "src.parsers.telegram.telegram_parser.TelegramAIExtractor",
                return_value=mock_extractor,
            ),
        ):
            await parser.connect()

        mock_client.start.assert_called_once()
        mock_extractor.connect.assert_called_once()
        assert parser._client is not None
        assert parser._extractor is not None

    @pytest.mark.asyncio
    async def test_context_manager_connects_and_disconnects(self, parser: TelegramParser) -> None:
        mock_client = AsyncMock()
        mock_extractor = AsyncMock()

        with (
            patch(
                "src.parsers.telegram.telegram_parser.TelegramClient",
                return_value=mock_client,
            ),
            patch(
                "src.parsers.telegram.telegram_parser.TelegramAIExtractor",
                return_value=mock_extractor,
            ),
        ):
            async with parser:
                assert parser._client is not None
                assert parser._extractor is not None

        mock_client.disconnect.assert_called_once()
        mock_extractor.disconnect.assert_called_once()


class TestDisconnect:
    @pytest.mark.asyncio
    async def test_disconnects_all_resources(self, parser: TelegramParser) -> None:
        mock_client = AsyncMock()
        mock_extractor = AsyncMock()

        parser._client = mock_client
        parser._extractor = mock_extractor

        await parser.disconnect()

        mock_client.disconnect.assert_called_once()
        mock_extractor.disconnect.assert_called_once()
        assert parser._client is None
        assert parser._extractor is None

    @pytest.mark.asyncio
    async def test_handles_already_disconnected(self, parser: TelegramParser) -> None:
        parser._client = None
        parser._extractor = None

        await parser.disconnect()


class TestEnsureClient:
    def test_returns_client_when_connected(self, parser: TelegramParser) -> None:
        mock_client = MagicMock()
        parser._client = mock_client

        result = parser._ensure_client()

        assert result == mock_client

    def test_raises_when_not_connected(self, parser: TelegramParser) -> None:
        parser._client = None

        with pytest.raises(RuntimeError, match="Telegram client not connected"):
            parser._ensure_client()


class TestEnsureExtractor:
    def test_returns_extractor_when_initialized(self, parser: TelegramParser) -> None:
        mock_extractor = MagicMock()
        parser._extractor = mock_extractor

        result = parser._ensure_extractor()

        assert result == mock_extractor

    def test_raises_when_not_initialized(self, parser: TelegramParser) -> None:
        parser._extractor = None

        with pytest.raises(RuntimeError, match="AI extractor not initialized"):
            parser._ensure_extractor()


class TestIterMessages:
    @pytest.mark.asyncio
    async def test_yields_messages_in_date_range(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        mock_message = MagicMock()
        mock_message.id = 12345
        mock_message.text = "Job posting"
        mock_message.date = datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC)

        with patch("src.parsers.telegram.telegram_parser.Message", type(mock_message)):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@channel", from_date, to_date):
                messages.append(msg)

        assert len(messages) == 1
        assert messages[0].id == 12345
        assert messages[0].text == "Job posting"

    @pytest.mark.asyncio
    async def test_skips_messages_without_text(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        mock_message_with_text = MagicMock()
        mock_message_with_text.id = 1
        mock_message_with_text.text = "Has text"
        mock_message_with_text.date = datetime(2024, 6, 15, tzinfo=UTC)

        mock_message_no_text = MagicMock()
        mock_message_no_text.id = 2
        mock_message_no_text.text = None
        mock_message_no_text.date = datetime(2024, 6, 15, tzinfo=UTC)

        with patch(
            "src.parsers.telegram.telegram_parser.Message",
            type(mock_message_with_text),
        ):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message_with_text
                yield mock_message_no_text

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@channel", from_date, to_date):
                messages.append(msg)

        assert len(messages) == 1
        assert messages[0].id == 1

    @pytest.mark.asyncio
    async def test_stops_on_message_before_from_date(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 15, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        mock_message_in_range = MagicMock()
        mock_message_in_range.id = 1
        mock_message_in_range.text = "In range"
        mock_message_in_range.date = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)

        mock_message_before = MagicMock()
        mock_message_before.id = 2
        mock_message_before.text = "Before range"
        mock_message_before.date = datetime(2024, 6, 14, 12, 0, 0, tzinfo=UTC)

        with patch(
            "src.parsers.telegram.telegram_parser.Message",
            type(mock_message_in_range),
        ):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message_in_range
                yield mock_message_before

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@channel", from_date, to_date):
                messages.append(msg)

        assert len(messages) == 1
        assert messages[0].id == 1

    @pytest.mark.asyncio
    async def test_skips_messages_after_to_date(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 15, tzinfo=UTC)

        class MockMessage:
            pass

        mock_message_after = MockMessage()
        mock_message_after.id = 1  # type: ignore[attr-defined]
        mock_message_after.text = "After range"  # type: ignore[attr-defined]
        mock_message_after.date = datetime(2024, 6, 16, tzinfo=UTC)  # type: ignore[attr-defined]

        mock_message_in_range = MockMessage()
        mock_message_in_range.id = 2  # type: ignore[attr-defined]
        mock_message_in_range.text = "In range"  # type: ignore[attr-defined]
        mock_message_in_range.date = datetime(2024, 6, 14, 12, 0, 0, tzinfo=UTC)  # type: ignore[attr-defined]

        mock_message_before = MockMessage()
        mock_message_before.id = 3  # type: ignore[attr-defined]
        mock_message_before.text = "Before range"  # type: ignore[attr-defined]
        mock_message_before.date = datetime(2024, 6, 13, tzinfo=UTC)  # type: ignore[attr-defined]

        with patch("src.parsers.telegram.telegram_parser.Message", MockMessage):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message_after
                yield mock_message_in_range
                yield mock_message_before

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@channel", from_date, to_date):
                messages.append(msg)

        assert len(messages) == 1
        assert messages[0].id == 2

    @pytest.mark.asyncio
    async def test_generates_correct_url(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        mock_message = MagicMock()
        mock_message.id = 12345
        mock_message.text = "Job"
        mock_message.date = datetime(2024, 6, 15, tzinfo=UTC)

        with patch("src.parsers.telegram.telegram_parser.Message", type(mock_message)):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@jobchannel", from_date, to_date):
                messages.append(msg)

        assert messages[0].url == "https://t.me/jobchannel/12345"

    @pytest.mark.asyncio
    async def test_strips_at_from_channel_name(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        mock_message = MagicMock()
        mock_message.id = 123
        mock_message.text = "Job"
        mock_message.date = datetime(2024, 6, 15, tzinfo=UTC)

        with patch("src.parsers.telegram.telegram_parser.Message", type(mock_message)):
            mock_client = AsyncMock()

            async def mock_iter(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
                yield mock_message

            mock_client.iter_messages = mock_iter
            parser._client = mock_client

            messages = []
            async for msg in parser._iter_messages("@testchannel", from_date, to_date):
                messages.append(msg)

        assert "@@" not in messages[0].url
        assert "testchannel" in messages[0].url


class TestStreamVacancies:
    @pytest.mark.asyncio
    async def test_yields_vacancies_in_batches(
        self,
        parser: TelegramParser,
        sample_extraction_result: ExtractionResult,
    ) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            for i in range(15):
                yield TelegramMessage(
                    id=i,
                    text=f"Job {i}",
                    date=datetime(2024, 6, 15, tzinfo=UTC),
                    channel="@channel",
                    url=f"https://t.me/channel/{i}",
                )

        mock_extractor = AsyncMock()
        mock_extractor.extract_vacancy = AsyncMock(return_value=sample_extraction_result)
        parser._extractor = mock_extractor

        with (
            patch.object(parser, "_iter_messages", mock_iter_messages),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            batches = []
            async for batch in parser.stream_vacancies("@channel", from_date, to_date):
                batches.append(batch)

        assert len(batches) == 2
        assert len(batches[0]) == 10
        assert len(batches[1]) == 5

    @pytest.mark.asyncio
    async def test_skips_failed_extractions(
        self,
        parser: TelegramParser,
        sample_extraction_result: ExtractionResult,
        failed_extraction_result: ExtractionResult,
    ) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            for i in range(3):
                yield TelegramMessage(
                    id=i,
                    text=f"Message {i}",
                    date=datetime(2024, 6, 15, tzinfo=UTC),
                    channel="@channel",
                    url=f"https://t.me/channel/{i}",
                )

        mock_extractor = AsyncMock()
        mock_extractor.extract_vacancy = AsyncMock(
            side_effect=[
                sample_extraction_result,
                failed_extraction_result,
                sample_extraction_result,
            ]
        )
        parser._extractor = mock_extractor

        with (
            patch.object(parser, "_iter_messages", mock_iter_messages),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            all_vacancies = []
            async for batch in parser.stream_vacancies("@channel", from_date, to_date):
                all_vacancies.extend(batch)

        assert len(all_vacancies) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_messages(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            return
            yield  # type: ignore[misc]

        mock_extractor = AsyncMock()
        parser._extractor = mock_extractor

        with patch.object(parser, "_iter_messages", mock_iter_messages):
            batches = []
            async for batch in parser.stream_vacancies("@channel", from_date, to_date):
                batches.append(batch)

        assert len(batches) == 0

    @pytest.mark.asyncio
    async def test_yields_remaining_batch_at_end(
        self,
        parser: TelegramParser,
        sample_extraction_result: ExtractionResult,
    ) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            for i in range(3):
                yield TelegramMessage(
                    id=i,
                    text=f"Job {i}",
                    date=datetime(2024, 6, 15, tzinfo=UTC),
                    channel="@channel",
                    url=f"https://t.me/channel/{i}",
                )

        mock_extractor = AsyncMock()
        mock_extractor.extract_vacancy = AsyncMock(return_value=sample_extraction_result)
        parser._extractor = mock_extractor

        with (
            patch.object(parser, "_iter_messages", mock_iter_messages),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            batches = []
            async for batch in parser.stream_vacancies("@channel", from_date, to_date):
                batches.append(batch)

        assert len(batches) == 1
        assert len(batches[0]) == 3

    @pytest.mark.asyncio
    async def test_respects_ai_delay(
        self,
        parser: TelegramParser,
        sample_extraction_result: ExtractionResult,
    ) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            yield TelegramMessage(
                id=1,
                text="Job",
                date=datetime(2024, 6, 15, tzinfo=UTC),
                channel="@channel",
                url="https://t.me/channel/1",
            )

        mock_extractor = AsyncMock()
        mock_extractor.extract_vacancy = AsyncMock(return_value=sample_extraction_result)
        parser._extractor = mock_extractor

        with (
            patch.object(parser, "_iter_messages", mock_iter_messages),
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            async for _ in parser.stream_vacancies("@channel", from_date, to_date):
                pass

        mock_sleep.assert_called_with(parser.AI_DELAY)

    @pytest.mark.asyncio
    async def test_handles_extraction_without_vacancy(self, parser: TelegramParser) -> None:
        from_date = datetime(2024, 6, 14, tzinfo=UTC)
        to_date = datetime(2024, 6, 16, tzinfo=UTC)

        partial_result = ExtractionResult(
            success=True,
            vacancy=None,
            error=None,
            raw_response="{}",
        )

        async def mock_iter_messages(
            *args: Any, **kwargs: Any
        ) -> AsyncGenerator[TelegramMessage, None]:
            yield TelegramMessage(
                id=1,
                text="Not a vacancy",
                date=datetime(2024, 6, 15, tzinfo=UTC),
                channel="@channel",
                url="https://t.me/channel/1",
            )

        mock_extractor = AsyncMock()
        mock_extractor.extract_vacancy = AsyncMock(return_value=partial_result)
        parser._extractor = mock_extractor

        with (
            patch.object(parser, "_iter_messages", mock_iter_messages),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            batches = []
            async for batch in parser.stream_vacancies("@channel", from_date, to_date):
                batches.append(batch)

        assert len(batches) == 0


class TestBatchSize:
    def test_default_batch_size(self, parser: TelegramParser) -> None:
        assert parser.BATCH_SIZE == 10

    def test_default_ai_delay(self, parser: TelegramParser) -> None:
        assert parser.AI_DELAY == 2


class TestInitialization:
    def test_initializes_with_none_values(self) -> None:
        parser = TelegramParser()

        assert parser._client is None
        assert parser._extractor is None
