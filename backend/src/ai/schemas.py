from dataclasses import dataclass


@dataclass(slots=True)
class AIMessage:
    role: str
    content: str


@dataclass(slots=True)
class UsageInfo:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(slots=True)
class RateLimitInfo:
    requests_limit: int | None = None
    tokens_limit: int | None = None
    requests_remaining: int | None = None
    tokens_remaining: int | None = None
    requests_reset: str | None = None
    tokens_reset: str | None = None


@dataclass(slots=True)
class AIResponse:
    content: str
    model: str
    usage: UsageInfo
    rate_limit: RateLimitInfo | None
    finish_reason: str
