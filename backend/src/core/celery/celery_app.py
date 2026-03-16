from typing import Any

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from kombu import Exchange, Queue

from src.core.config import rabbitmq_config
from src.core.logger import logger as app_logger

celery_app = Celery(
    "vacancy_monitoring",
    broker=rabbitmq_config.amqp_url,
    backend="rpc://",
)

vacancy_exchange = Exchange("vacancy_exchange", type="direct")
vacancy_dlx = Exchange("vacancy_dlx", type="direct")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_queues=(
        Queue(
            "parsing_queue",
            exchange=vacancy_exchange,
            routing_key="parsing",
            queue_arguments={
                "x-dead-letter-exchange": "vacancy_dlx",
                "x-dead-letter-routing-key": "parsing_dlq",
            },
        ),
        Queue(
            "import_queue",
            exchange=vacancy_exchange,
            routing_key="import",
            queue_arguments={
                "x-dead-letter-exchange": "vacancy_dlx",
                "x-dead-letter-routing-key": "import_dlq",
            },
        ),
        Queue(
            "parsing_dlq",
            exchange=vacancy_dlx,
            routing_key="parsing_dlq",
        ),
        Queue(
            "import_dlq",
            exchange=vacancy_dlx,
            routing_key="import_dlq",
        ),
    ),
)

celery_app.autodiscover_tasks(["src.core.celery.tasks"])


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logger(
    *args: tuple,
    logger: Any = None,
    **kwargs: dict[str, Any],
) -> None:
    if logger is None:
        return

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if app_logger.handlers:
        logger.addHandler(app_logger.handlers[0])
