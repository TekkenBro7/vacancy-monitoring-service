from abc import ABC, abstractmethod
from datetime import datetime

from src.parsers.services.parser_import_service import ParserImportService


class BaseVacancyService(ABC):
    def __init__(self, import_service: ParserImportService):
        self.import_service = import_service

    @abstractmethod
    async def run(
        self,
        query: str | None,
        from_date: datetime,
        to_date: datetime,
    ) -> None:
        pass
