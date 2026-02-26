import aio_pika
from aio_pika import RobustChannel, RobustConnection

from src.core.config import rabbitmq_config
from src.core.logger import logger


class RabbitMQ:
    _connection: RobustConnection | None = None
    _channel: RobustChannel | None = None

    @classmethod
    async def connect(cls) -> None:
        if cls._connection and not cls._connection.is_closed:
            return

        logger.info("Connecting to RabbitMQ...")

        cls._connection = await aio_pika.connect_robust(rabbitmq_config.amqp_url)  # type: ignore

        cls._channel = await cls._connection.channel()  # type: ignore
        assert cls._channel is not None

        await cls._channel.set_qos(prefetch_count=10)

        logger.info("RabbitMQ connected")

    @classmethod
    async def get_channel(cls) -> RobustChannel:
        if not cls._channel or cls._channel.is_closed:
            await cls.connect()  # type: ignore

        return cls._channel  # type: ignore

    @classmethod
    async def close(cls) -> None:
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            logger.info("RabbitMQ connection closed")
