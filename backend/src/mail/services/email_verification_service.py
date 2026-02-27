import random

import redis

from src.core.celery.tasks import send_verification_email_task
from src.core.constants import EMAIL_VERIFICATION_CODE_TTL, EMAIL_VERIFICATION_PREFIX
from src.core.logger import logger
from src.core.redis_client import redis_client
from src.utils.redis_keys import RedisKeys


class EmailVerificationService:
    @classmethod
    async def send_code(cls, email: str, purpose: str) -> None:
        try:
            logger.info(
                "Sending verification code email=%s purpose=%s",
                email,
                purpose,
            )

            code = cls._generate_code()

            await redis_client.set(
                RedisKeys.verification(email, purpose),
                code,
                ex=EMAIL_VERIFICATION_CODE_TTL,
            )
            send_verification_email_task.delay(email, code)

            logger.info(
                "Verification code stored and sent email=%s purpose=%s",
                email,
                purpose,
            )

        except redis.RedisError as e:
            logger.error(
                "Redis error sending code email=%s purpose=%s error=%s",
                email,
                purpose,
                e,
            )
            raise
        except Exception as e:
            logger.exception(
                "Unexpected error sending code email=%s purpose=%s", email, purpose, str(e)
            )
            raise

    @classmethod
    async def verify_code(cls, email: str, code: str, purpose: str) -> bool:
        try:
            logger.info(
                "Verifying code email=%s purpose=%s",
                email,
                purpose,
            )

            stored = await redis_client.get(f"{EMAIL_VERIFICATION_PREFIX}:{purpose}:{email}")

            if stored is None:
                logger.warning(
                    "Verification code not found email=%s purpose=%s",
                    email,
                    purpose,
                )
                return False

            is_valid = stored == code
            if is_valid:
                logger.info(
                    "Verification successful email=%s purpose=%s",
                    email,
                    purpose,
                )
                await redis_client.delete(f"{EMAIL_VERIFICATION_PREFIX}:{purpose}{email}")
            else:
                logger.warning(
                    "Verification failed email=%s purpose=%s expected=%s got=%s",
                    email,
                    purpose,
                    stored,
                    code,
                )

            return is_valid

        except redis.RedisError as e:
            logger.error(
                "Redis error verifying email=%s purpose=%s error=%s",
                email,
                purpose,
                e,
            )
            return False

        except Exception:
            logger.exception(
                "Unexpected verification error email=%s purpose=%s",
                email,
                purpose,
            )
            return False

    @staticmethod
    def _generate_code() -> str:
        return str(random.randint(100000, 999999))
