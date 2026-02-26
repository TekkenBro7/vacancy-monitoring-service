from src.core.celery.celery_app import celery_app
from src.core.logger import logger


@celery_app.task
def test_task(message: str) -> str:
    logger.info(f"🔥 Test task received message: {message}")
    return f"Task done: {message}"
