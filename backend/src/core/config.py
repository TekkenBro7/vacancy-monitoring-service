import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("APP_PORT", 8000))
    RELOAD: bool = os.getenv("APP_RELOAD", "True").lower() in ("true", "1")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
    CORS_METHODS = os.getenv("CORS_METHODS", "").split(",")
    CORS_HEADERS = os.getenv("CORS_HEADERS", "").split(",")
    FRONTEND_URL = os.getenv("FRONTEND_URL")


class PostgresConfig:
    HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    PORT: str = os.getenv("POSTGRES_PORT", "5432")
    USER: str = os.getenv("POSTGRES_USER", "postgres")
    PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("POSTGRES_DB", "postgres")
    TEST_DB_NAME: str = os.getenv("POSTGRES_TEST_DB", "test_db")

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.DB_NAME}"
        )

    @property
    def async_test_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.TEST_DB_NAME}"
        )


class JWTConfig:
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_EXPIRE_SECONDS = int(os.getenv("JWT_ACCESS_EXPIRE_SECONDS", "3600"))
    JWT_REFRESH_EXPIRE_SECONDS = int(os.getenv("JWT_REFRESH_EXPIRE_SECONDS", "2592000"))

    JWT_REFRESH_COOKIE_NAME = os.getenv("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    JWT_REFRESH_COOKIE_HTTPONLY = os.getenv("JWT_REFRESH_COOKIE_HTTPONLY", "True").lower() in (
        "true",
        "1",
    )
    JWT_REFRESH_COOKIE_SECURE = os.getenv("JWT_REFRESH_COOKIE_SECURE", "False").lower() in (
        "true",
        "1",
    )
    JWT_REFRESH_COOKIE_SAMESITE = os.getenv("JWT_REFRESH_COOKIE_SAMESITE", "lax")
    JWT_REFRESH_COOKIE_PATH = os.getenv("JWT_REFRESH_COOKIE_PATH", "/api/v1/auth/")


class OAuthConfig:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


class RabbitMQConfig:
    HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    USER: str = os.getenv("RABBITMQ_USER", "guest")
    PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    VHOST: str = os.getenv("RABBITMQ_VHOST", "/")

    @property
    def amqp_url(self) -> str:
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.VHOST}"


class RedisConfig:
    HOST: str = os.getenv("REDIS_HOST", "localhost")
    PORT: int = int(os.getenv("REDIS_PORT", 6379))
    DB: int = int(os.getenv("REDIS_DB", 0))
    PASSWORD: str | None = os.getenv("REDIS_PASSWORD")

    @property
    def redis_url(self) -> str:
        if self.PASSWORD:
            return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"


class MailConfig:
    USERNAME: str = os.getenv("MAIL_USERNAME", "")
    PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    FROM: str = os.getenv("MAIL_FROM", "")
    FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Vacancy Monitoring")
    SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    PORT: int = int(os.getenv("MAIL_PORT", 587))
    STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    TEMPLATE_FOLDER: str = os.getenv("MAIL_TEMPLATE_FOLDER", "src/templates/email")


class HHConfig:
    HH_SOURCE_NAME = "HeadHunter"
    HH_BASE_URL = "https://api.hh.ru/vacancies"
    HH_MAX_TOTAL = 2000
    HH_PER_PAGE = 100
    HH_TIMEOUT = int(os.getenv("HH_TIMEOUT", 20))
    HH_RETRIES = int(os.getenv("HH_RETRIES", 3))


class SuperJobConfig:
    SJ_SOURCE_NAME = "SuperJob"
    SJ_API_KEY: str = os.getenv("SUPERJOB_API_KEY", "")
    SJ_BASE_URL = "https://api.superjob.ru/2.0/vacancies"
    SJ_MAX_TOTAL = 480
    SJ_MAX_PAGES = 12
    SJ_PER_PAGE = 40
    SJ_TIMEOUT = int(os.getenv("SJ_TIMEOUT", "20"))
    SJ_RETRIES = int(os.getenv("SJ_RETRIES", "3"))
    SJ_RATE_LIMIT_DELAY = 0.4


class PracaByConfig:
    PRACA_SOURCE_NAME = "PracaBy"
    PRACA_BASE_URL = "https://praca.by"
    PRACA_SEARCH_URL = "https://praca.by/search/vacancies/"
    PRACA_TIMEOUT = int(os.getenv("PRACA_TIMEOUT", "30"))
    PRACA_RETRIES = int(os.getenv("PRACA_RETRIES", "3"))
    PRACA_RATE_LIMIT_DELAY = 0
    PRACA_PER_PAGE = 20
    PRACA_MAX_PAGES: int = 550


class EpamConfig:
    EPAM_SOURCE_NAME: str = "EPAM"
    EPAM_BASE_URL: str = "https://careers.epam.com"
    EPAM_SEARCH_URL: str = "https://careers.epam.com/en/jobs"

    EPAM_TIMEOUT: int = int(os.getenv("EPAM_TIMEOUT", "30"))
    EPAM_RETRIES: int = int(os.getenv("EPAM_RETRIES", "3"))
    EPAM_RATE_LIMIT_DELAY: float = 0
    EPAM_MAX_PAGES: int = 500
    EPAM_PAGE_SIZE: int = 10


base_config = BaseConfig()
postgres_config = PostgresConfig()
jwt_config = JWTConfig()
oauth_config = OAuthConfig()
rabbitmq_config = RabbitMQConfig()
redis_config = RedisConfig()
mail_config = MailConfig()
super_job_config = SuperJobConfig()
hh_config = HHConfig()
praca_config = PracaByConfig()
epam_config = EpamConfig()
