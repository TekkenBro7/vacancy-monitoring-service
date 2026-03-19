from typing import Any

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger
from kombu import Exchange, Queue

from src.core.config import rabbitmq_config
from src.core.logger import logger as app_logger

celery_app = Celery(
    "vacancy_monitoring",
    broker=rabbitmq_config.amqp_url,
)

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
    worker_hijack_root_logger=False,
)

vacancy_exchange = Exchange("vacancy_exchange", type="direct")

celery_app.conf.task_queues = (
    Queue("celery"),
    Queue(
        "parsing_queue",
        exchange=vacancy_exchange,
        routing_key="parsing",
    ),
    Queue(
        "import_queue",
        exchange=vacancy_exchange,
        routing_key="import",
    ),
    Queue("mail_queue"),
)

celery_app.conf.task_routes = {
    "run_source_parse_task": {"queue": "parsing_queue", "routing_key": "parsing"},
    "schedule_source_parse_tasks": {"queue": "parsing_queue", "routing_key": "parsing"},
    "dispatch_source_parse_tasks": {"queue": "parsing_queue"},
    "import_vacancies_batch": {"queue": "import_queue", "routing_key": "import"},
    "send_verification_email": {"queue": "mail_queue", "routing_key": "mail"},
}


celery_app.conf.beat_schedule = {
    "schedule-source-parse-daily": {
        "task": "schedule_source_parse_tasks",
        "schedule": crontab(hour=2, minute=0),
    },
    "dispatch-source-parse-tasks": {
        "task": "dispatch_source_parse_tasks",
        "schedule": crontab(minute="*/1"),
    },
}


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logger(
    *args: tuple,
    logger: Any = None,
    **kwargs: dict[str, Any],
) -> None:
    if logger is None:
        return

    logger.handlers.clear()

    for handler in app_logger.handlers:
        logger.addHandler(handler)

    logger.setLevel(app_logger.level)
    logger.propagate = False


celery_app.autodiscover_tasks(["src.core.celery.tasks"])
