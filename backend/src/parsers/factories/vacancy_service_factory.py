from src.core.config import hh_config, super_job_config
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.hh_ru.hh_service import HHVacancyService
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.superjob.sj_service import SJVacancyService


class VacancyServiceFactory:
    @staticmethod
    def create(
        source_name: str,
        import_service: ParserImportService,
    ) -> BaseVacancyService:
        if source_name == hh_config.HH_SOURCE_NAME:
            return HHVacancyService(import_service)
        elif source_name == super_job_config.SJ_SOURCE_NAME:
            return SJVacancyService(import_service)
        else:
            raise ValueError(f"Unsupported source: {source_name}")
