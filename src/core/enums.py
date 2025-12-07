from enum import Enum


class PostgresErrorCode(str, Enum):
    FOREIGN_KEY_VIOLATION = "23503"
