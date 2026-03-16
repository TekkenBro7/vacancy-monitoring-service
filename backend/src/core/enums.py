from enum import Enum


class PostgresErrorCode(str, Enum):
    FOREIGN_KEY_VIOLATION = "23503"


class VerificationPurpose(str, Enum):
    REGISTER = "register"
    ADD_PASSWORD = "add_password"


class HHWorkFormat(str, Enum):
    REMOTE = "REMOTE"


class SourceParseTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
