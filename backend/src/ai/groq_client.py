from dataclasses import dataclass
from types import TracebackType
from typing import Any

from groq import APIError, AsyncGroq, RateLimitError
from groq.types.chat import ChatCompletionMessageParam

from src.core.config import ai_config
from src.core.logger import logger


@dataclass
class AIMessage:
    role: str
    content: str


@dataclass
class UsageInfo:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class RateLimitInfo:
    requests_limit: int | None = None
    tokens_limit: int | None = None
    requests_remaining: int | None = None
    tokens_remaining: int | None = None
    requests_reset: str | None = None
    tokens_reset: str | None = None


@dataclass
class AIResponse:
    content: str
    model: str
    usage: UsageInfo
    rate_limit: RateLimitInfo | None
    finish_reason: str


class GroqClient:
    DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
    ):
        self._api_key = ai_config.GROQ_API_KEY
        self._model = model
        self._client: AsyncGroq | None = None

    async def __aenter__(self) -> "GroqClient":
        self._client = AsyncGroq(api_key=self._api_key)
        logger.info("GroqClient initialized")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._client:
            await self._client.close()
            self._client = None
        logger.info("GroqClient session closed")

    def _ensure_client(self) -> AsyncGroq:
        if self._client is None:
            raise RuntimeError("GroqClient не инициализирован")
        return self._client

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _extract_usage(self, response: Any) -> UsageInfo:
        usage = response.usage
        return UsageInfo(
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    def _extract_rate_limit(self, headers: Any) -> RateLimitInfo | None:
        if headers is None:
            return None

        def get_header(name: str) -> str | None:
            value = headers.get(name)
            if value is None:
                return None
            if isinstance(value, bytes):
                return value.decode("utf-8")
            return str(value)

        return RateLimitInfo(
            requests_limit=self._safe_int(get_header("x-ratelimit-limit-requests")),
            tokens_limit=self._safe_int(get_header("x-ratelimit-limit-tokens")),
            requests_remaining=self._safe_int(get_header("x-ratelimit-remaining-requests")),
            tokens_remaining=self._safe_int(get_header("x-ratelimit-remaining-tokens")),
            requests_reset=get_header("x-ratelimit-reset-requests"),
            tokens_reset=get_header("x-ratelimit-reset-tokens"),
        )

    async def chat(
        self,
        content: str,
        system_prompt: str | None = None,
    ) -> AIResponse:
        client = self._ensure_client()

        messages: list[ChatCompletionMessageParam] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})

        try:
            raw_response = await client.chat.completions.with_raw_response.create(
                model=self._model,
                messages=messages,
                temperature=ai_config.GROQ_TEMPERATURE,
                max_tokens=ai_config.GROQ_MAX_TOKENS,
            )

            response = await raw_response.parse()
            choice = response.choices[0]

            usage = self._extract_usage(response)
            rate_limit = self._extract_rate_limit(raw_response.headers)

            logger.info(
                "Groq request: model=%s, tokens=%d (prompt=%d, completion=%d)",
                self._model,
                usage.total_tokens,
                usage.prompt_tokens,
                usage.completion_tokens,
            )

            if rate_limit:
                logger.info(
                    "Rate limits: requests=%s/%s (reset=%s), tokens=%s/%s (reset=%s)",
                    rate_limit.requests_remaining,
                    rate_limit.requests_limit,
                    rate_limit.requests_reset,
                    rate_limit.tokens_remaining,
                    rate_limit.tokens_limit,
                    rate_limit.tokens_reset,
                )

            return AIResponse(
                content=choice.message.content or "",
                model=self._model,
                usage=usage,
                rate_limit=rate_limit,
                finish_reason=choice.finish_reason or "unknown",
            )

        except RateLimitError as e:
            logger.error("Rate limit exceeded: %s", e)
            raise

        except APIError as e:
            logger.error("Groq API error: %s", e)
            raise
