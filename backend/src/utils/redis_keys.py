import hashlib
import json

from src.core.constants import EMAIL_PENDING_PREFIX, EMAIL_VERIFICATION_PREFIX


class RedisKeys:
    @staticmethod
    def verification(email: str, purpose: str) -> str:
        return f"{EMAIL_VERIFICATION_PREFIX}:{purpose}:{email}"

    @staticmethod
    def pending(email: str, purpose: str) -> str:
        return f"{EMAIL_PENDING_PREFIX}:{purpose}:{email}"

    @staticmethod
    def company_key(name: str) -> str:
        return f"company:{name}"

    @staticmethod
    def city_key(name: str) -> str:
        return f"city:{name}"

    @staticmethod
    def currency_key(code: str) -> str:
        return f"currency:{code}"

    @staticmethod
    def source_key(name: str) -> str:
        return f"source:{name}"

    @staticmethod
    def vacancy_external_key(source_id: int, external_id: str) -> str:
        return f"vacancy:{source_id}:{external_id}"

    @staticmethod
    def vacancy_search_key(
        filters_dict: dict, page: int, page_size: int, include_filters: bool
    ) -> str:
        payload = {
            "filters": filters_dict,
            "page": page,
            "page_size": page_size,
            "include_filters": include_filters,
        }
        raw = json.dumps(payload, sort_keys=True, default=str)
        hashed = hashlib.md5(raw.encode()).hexdigest()
        return f"vacancy_search:{hashed}"
