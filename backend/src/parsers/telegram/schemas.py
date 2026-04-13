from dataclasses import dataclass
from datetime import datetime

from src.parsers.base.parser_result import ParserVacancyResult


@dataclass
class TelegramMessage:
    id: int
    text: str
    date: datetime
    channel: str
    url: str


@dataclass
class ExtractionResult:
    vacancy: ParserVacancyResult | None
    raw_response: str
    success: bool
    error: str | None = None
