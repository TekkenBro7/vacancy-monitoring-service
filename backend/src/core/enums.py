from enum import Enum, IntEnum


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


class SJPlaceOfWork(IntEnum):
    ANY = 0
    ON_SITE = 1  # на территории работодателя
    REMOTE = 2  # на дому (удалённо)
    TRAVEL = 3  # разъездного характера


class SJTypeOfWork(IntEnum):
    FULL_DAY = 6  # полный день
    PART_DAY = 10  # неполный день
    SHIFT = 12  # сменный график
    PART_TIME = 13  # частичная занятость
    TEMPORARY = 7  # временная работа
    ROTATION = 9  # вахтовым методом


class SJExperience(IntEnum):
    NO_EXPERIENCE = 1  # без опыта
    FROM_1_YEAR = 2  # от 1 года
    FROM_3_YEARS = 3  # от 3 лет
    FROM_6_YEARS = 4  # от 6 лет
