import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.ai.groq_client import AIResponse, RateLimitInfo, UsageInfo
from src.parsers.base.parser_result import ParserVacancyResult
from src.parsers.telegram.schemas import TelegramMessage
from src.parsers.telegram.telegram_ai_extractor import TelegramAIExtractor


@pytest.fixture
def extractor() -> TelegramAIExtractor:
    return TelegramAIExtractor()


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
def valid_ai_response_content() -> str:
    return json.dumps(
        {
            "external_id": "12345",
            "title": "Python Developer",
            "description": "<p>Looking for experienced developer</p>",
            "company_name": "TechCorp",
            "company_external_id": "tech_123",
            "salary_from": 3000,
            "salary_to": 5000,
            "currency": "USD",
            "city": "Remote",
            "address": None,
            "is_remote": True,
            "experience": "2+ years",
            "education": None,
            "employment": "Full-time",
            "schedule": "Remote",
            "internship": False,
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        }
    )


@pytest.fixture
def mock_ai_response(valid_ai_response_content: str) -> AIResponse:
    return AIResponse(
        content=valid_ai_response_content,
        model="llama-3.3-70b-versatile",
        usage=UsageInfo(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        rate_limit=RateLimitInfo(),
        finish_reason="stop",
    )


class TestConnect:
    @pytest.mark.asyncio
    async def test_creates_and_connects_client(self, extractor: TelegramAIExtractor) -> None:
        mock_client = AsyncMock()

        with patch(
            "src.parsers.telegram.telegram_ai_extractor.GroqClient",
            return_value=mock_client,
        ):
            await extractor.connect()

        mock_client.__aenter__.assert_called_once()
        assert extractor._client is not None

    @pytest.mark.asyncio
    async def test_logs_connection(self, extractor: TelegramAIExtractor) -> None:
        mock_client = AsyncMock()

        with (
            patch(
                "src.parsers.telegram.telegram_ai_extractor.GroqClient",
                return_value=mock_client,
            ),
            patch("src.parsers.telegram.telegram_ai_extractor.logger") as mock_logger,
        ):
            await extractor.connect()

        mock_logger.info.assert_called_with("AI extractor connected")


class TestDisconnect:
    @pytest.mark.asyncio
    async def test_disconnects_client(self, extractor: TelegramAIExtractor) -> None:
        mock_client = AsyncMock()
        extractor._client = mock_client

        await extractor.disconnect()

        mock_client.__aexit__.assert_called_once_with(None, None, None)
        assert extractor._client is None

    @pytest.mark.asyncio
    async def test_handles_already_disconnected(self, extractor: TelegramAIExtractor) -> None:
        extractor._client = None

        # Should not raise
        await extractor.disconnect()

    @pytest.mark.asyncio
    async def test_logs_disconnection(self, extractor: TelegramAIExtractor) -> None:
        mock_client = AsyncMock()
        extractor._client = mock_client

        with patch("src.parsers.telegram.telegram_ai_extractor.logger") as mock_logger:
            await extractor.disconnect()

        mock_logger.info.assert_called_with("AI extractor disconnected")


class TestEnsureClient:
    def test_returns_client_when_connected(self, extractor: TelegramAIExtractor) -> None:
        mock_client = MagicMock()
        extractor._client = mock_client

        result = extractor._ensure_client()

        assert result == mock_client

    def test_raises_when_not_connected(self, extractor: TelegramAIExtractor) -> None:
        extractor._client = None

        with pytest.raises(RuntimeError, match="AI client not connected"):
            extractor._ensure_client()


class TestExtractVacancy:
    @pytest.mark.asyncio
    async def test_successful_extraction(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
        mock_ai_response: AIResponse,
    ) -> None:
        mock_client = AsyncMock()
        mock_client.chat = AsyncMock(return_value=mock_ai_response)
        extractor._client = mock_client

        result = await extractor.extract_vacancy(sample_message)

        assert result.success is True
        assert result.vacancy is not None
        assert result.vacancy.title == "Python Developer"
        assert result.vacancy.company_name == "TechCorp"
        assert result.raw_response == mock_ai_response.content

    @pytest.mark.asyncio
    async def test_calls_chat_with_correct_params(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
        mock_ai_response: AIResponse,
    ) -> None:
        mock_client = AsyncMock()
        mock_client.chat = AsyncMock(return_value=mock_ai_response)
        extractor._client = mock_client

        with patch(
            "src.parsers.telegram.telegram_ai_extractor.VACANCY_EXTRACTION_PROMPT",
            "test_prompt",
        ):
            await extractor.extract_vacancy(sample_message)

        mock_client.chat.assert_called_once_with(
            content=sample_message.text,
            system_prompt="test_prompt",
        )

    @pytest.mark.asyncio
    async def test_handles_ai_error(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        mock_client = AsyncMock()
        mock_client.chat = AsyncMock(side_effect=Exception("API Error"))
        extractor._client = mock_client

        result = await extractor.extract_vacancy(sample_message)

        assert result.success is False
        assert result.vacancy is None
        assert result.error == "API Error"
        assert result.raw_response == ""

    @pytest.mark.asyncio
    async def test_handles_missing_title(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        response_without_title = AIResponse(
            content=json.dumps({"company_name": "TechCorp"}),
            model="test",
            usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            rate_limit=None,
            finish_reason="stop",
        )

        mock_client = AsyncMock()
        mock_client.chat = AsyncMock(return_value=response_without_title)
        extractor._client = mock_client

        result = await extractor.extract_vacancy(sample_message)

        assert result.success is False
        assert result.vacancy is None

    @pytest.mark.asyncio
    async def test_handles_invalid_json(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        invalid_response = AIResponse(
            content="This is not valid JSON",
            model="test",
            usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            rate_limit=None,
            finish_reason="stop",
        )

        mock_client = AsyncMock()
        mock_client.chat = AsyncMock(return_value=invalid_response)
        extractor._client = mock_client

        result = await extractor.extract_vacancy(sample_message)

        assert result.success is False
        assert result.vacancy is None


class TestParseAiResponse:
    def test_parses_complete_response(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
        valid_ai_response_content: str,
    ) -> None:
        result = extractor._parse_ai_response(valid_ai_response_content, sample_message)

        assert result is not None
        assert isinstance(result, ParserVacancyResult)
        assert result.external_id == "12345"
        assert result.title == "Python Developer"
        assert result.company_name == "TechCorp"
        assert result.salary_from == 3000
        assert result.salary_to == 5000
        assert result.currency == "USD"
        assert result.is_remote is True
        assert result.skills == ["Python", "FastAPI", "PostgreSQL"]

    def test_generates_external_id_when_missing(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"title": "Developer"})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is not None
        assert result.external_id == "tg_jobchannel_12345"

    def test_returns_none_when_title_missing(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"company_name": "TechCorp"})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is None

    def test_returns_none_on_invalid_json(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = "not valid json"

        result = extractor._parse_ai_response(content, sample_message)

        assert result is None

    def test_sets_vacancy_url_from_message(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"title": "Developer"})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is not None
        assert result.vacancy_url == sample_message.url

    def test_sets_dates_from_message(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"title": "Developer"})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is not None
        assert result.published_at == sample_message.date
        assert result.created_at == sample_message.date

    def test_handles_empty_skills(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"title": "Developer", "skills": None})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is not None
        assert result.skills == []

    def test_converts_external_id_to_string(
        self,
        extractor: TelegramAIExtractor,
        sample_message: TelegramMessage,
    ) -> None:
        content = json.dumps({"title": "Developer", "external_id": 99999})

        result = extractor._parse_ai_response(content, sample_message)

        assert result is not None
        assert result.external_id == "99999"
        assert isinstance(result.external_id, str)

    def test_strips_at_from_channel_in_generated_id(
        self,
        extractor: TelegramAIExtractor,
    ) -> None:
        message = TelegramMessage(
            id=123,
            text="Job",
            date=datetime(2024, 6, 15, tzinfo=UTC),
            channel="@testchannel",
            url="https://t.me/testchannel/123",
        )
        content = json.dumps({"title": "Developer"})

        result = extractor._parse_ai_response(content, message)

        assert result is not None
        assert result.external_id == "tg_testchannel_123"
        assert "@" not in result.external_id


class TestExtractJson:
    def test_extracts_plain_json(self, extractor: TelegramAIExtractor) -> None:
        content = '{"title": "Developer"}'

        result = extractor._extract_json(content)

        assert result == {"title": "Developer"}

    def test_extracts_json_with_markdown_code_block(self, extractor: TelegramAIExtractor) -> None:
        content = '```json\n{"title": "Developer"}\n```'

        result = extractor._extract_json(content)

        assert result == {"title": "Developer"}

    def test_extracts_json_with_plain_code_block(self, extractor: TelegramAIExtractor) -> None:
        content = '```\n{"title": "Developer"}\n```'

        result = extractor._extract_json(content)

        assert result == {"title": "Developer"}

    def test_handles_whitespace(self, extractor: TelegramAIExtractor) -> None:
        content = '  \n  {"title": "Developer"}  \n  '

        result = extractor._extract_json(content)

        assert result == {"title": "Developer"}

    def test_handles_code_block_without_newline(self, extractor: TelegramAIExtractor) -> None:
        content = '```{"title": "Developer"}```'

        result = extractor._extract_json(content)

        assert result == {"title": "Developer"}

    def test_raises_on_invalid_json(self, extractor: TelegramAIExtractor) -> None:
        content = "not valid json"

        with pytest.raises(json.JSONDecodeError):
            extractor._extract_json(content)

    def test_extracts_complex_json(self, extractor: TelegramAIExtractor) -> None:
        content = """```json
{
    "title": "Python Developer",
    "salary_from": 3000,
    "skills": ["Python", "FastAPI"],
    "is_remote": true
}
```"""

        result = extractor._extract_json(content)

        assert result["title"] == "Python Developer"
        assert result["salary_from"] == 3000
        assert result["skills"] == ["Python", "FastAPI"]
        assert result["is_remote"] is True


class TestSafeInt:
    def test_converts_int(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int(42) == 42

    def test_converts_string_int(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int("42") == 42

    def test_converts_float(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int(42.9) == 42

    def test_returns_none_for_none(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int(None) is None

    def test_returns_none_for_invalid_string(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int("not a number") is None

    def test_returns_none_for_empty_string(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int("") is None

    def test_returns_none_for_dict(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int({}) is None

    def test_returns_none_for_list(self, extractor: TelegramAIExtractor) -> None:
        assert extractor._safe_int([]) is None


class TestInitialization:
    def test_initializes_with_none_client(self) -> None:
        extractor = TelegramAIExtractor()

        assert extractor._client is None
