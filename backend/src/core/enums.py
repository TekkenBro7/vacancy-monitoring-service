from enum import Enum


class PostgresErrorCode(str, Enum):
    FOREIGN_KEY_VIOLATION = "23503"


class VerificationPurpose(str, Enum):
    REGISTER = "register"
    ADD_PASSWORD = "add_password"
