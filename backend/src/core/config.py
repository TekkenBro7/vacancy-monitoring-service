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
    JWT_REFRESH_COOKIE_HTTPONLY = bool(os.getenv("JWT_REFRESH_COOKIE_HTTPONLY", True))
    JWT_REFRESH_COOKIE_SECURE = bool(os.getenv("JWT_REFRESH_COOKIE_SECURE", False))
    JWT_REFRESH_COOKIE_SAMESITE = os.getenv("JWT_REFRESH_COOKIE_SAMESITE", "strict")
    JWT_REFRESH_COOKIE_PATH = os.getenv("JWT_REFRESH_COOKIE_PATH", "/api/v1/auth/refresh")


class OAuthConfig:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


base_config = BaseConfig()
postgres_config = PostgresConfig()
jwt_config = JWTConfig()
oauth_config = OAuthConfig()
