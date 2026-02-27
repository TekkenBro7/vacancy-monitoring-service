from src.core.constants import EMAIL_PENDING_PREFIX, EMAIL_VERIFICATION_PREFIX


class RedisKeys:
    @staticmethod
    def verification(email: str, purpose: str) -> str:
        return f"{EMAIL_VERIFICATION_PREFIX}:{purpose}:{email}"

    @staticmethod
    def pending(email: str, purpose: str) -> str:
        return f"{EMAIL_PENDING_PREFIX}:{purpose}:{email}"
