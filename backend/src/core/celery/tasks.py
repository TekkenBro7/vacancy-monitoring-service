import asyncio

from fastapi_mail import FastMail, MessageSchema, MessageType, NameEmail

from src.core.celery.celery_app import celery_app
from src.core.logger import logger
from src.mail.connection import mail_connection


@celery_app.task(name="send_verification_email")
def send_verification_email_task(email: str, code: str) -> None:
    async def _send() -> None:
        fm = FastMail(mail_connection)

        message = MessageSchema(
            subject="Verification Code",
            recipients=[NameEmail("", email=email)],
            template_body={"code": code},
            subtype=MessageType.html,
        )

        await fm.send_message(message, template_name="verification.html")

    try:
        asyncio.run(_send())
        logger.info(
            "Verification email sent email=%s",
            email,
        )
    except Exception as e:
        logger.exception(
            "Failed to send verification email email=%s error=%s",
            email,
            e,
        )
        raise
