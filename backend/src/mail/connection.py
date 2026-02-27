from pathlib import Path

from fastapi_mail import ConnectionConfig
from pydantic import SecretStr

from src.core.config import mail_config

mail_connection = ConnectionConfig(
    MAIL_USERNAME=mail_config.USERNAME,
    MAIL_PASSWORD=SecretStr(mail_config.PASSWORD),
    MAIL_FROM=mail_config.FROM,
    MAIL_FROM_NAME=mail_config.FROM_NAME,
    MAIL_PORT=mail_config.PORT,
    MAIL_SERVER=mail_config.SERVER,
    MAIL_STARTTLS=mail_config.STARTTLS,
    MAIL_SSL_TLS=mail_config.SSL_TLS,
    TEMPLATE_FOLDER=Path(mail_config.TEMPLATE_FOLDER),
)
