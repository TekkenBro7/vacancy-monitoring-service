from abc import ABC, abstractmethod

from src.parsers.base.parser_result import ParserVacancyResult


class ParserInterface(ABC):
    @abstractmethod
    async def search_vacancies(self, query: str) -> list[ParserVacancyResult]:
        pass
