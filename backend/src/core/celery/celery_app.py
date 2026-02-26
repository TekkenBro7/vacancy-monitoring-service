from typing import Any

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from src.core.config import rabbitmq_config
from src.core.logger import logger as app_logger

celery_app = Celery(
    "vacancy_monitoring",
    broker=rabbitmq_config.amqp_url,
    backend="rpc://",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logger(*args: tuple, logger: Any = None, **kwargs: dict[str, Any]) -> None:
    if logger is None:
        return
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    logger.addHandler(app_logger.handlers[0])
