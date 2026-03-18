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
