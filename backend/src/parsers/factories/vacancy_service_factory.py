from src.core.config import epam_config, hh_config, praca_config, super_job_config, wargaming_config
from src.parsers.base.base_vacancy_service import BaseVacancyService
from src.parsers.epam.epam_service import EpamVacancyService
from src.parsers.hh_ru.hh_service import HHVacancyService
from src.parsers.praca_by.praca_service import PracaByVacancyService
from src.parsers.services.parser_import_service import ParserImportService
from src.parsers.superjob.sj_service import SJVacancyService
from src.parsers.wargaming.wargaming_service import WargamingVacancyService


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
        elif source_name == praca_config.PRACA_SOURCE_NAME:
            return PracaByVacancyService(import_service)
        elif source_name == epam_config.EPAM_SOURCE_NAME:
            return EpamVacancyService(import_service)
        elif source_name == wargaming_config.WARGAMING_SOURCE_NAME:
            return WargamingVacancyService(import_service)
        else:
            raise ValueError(f"Unsupported source: {source_name}")
