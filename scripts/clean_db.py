import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.database.session import get_async_session


async def clear_db(session: AsyncSession) -> None:
    logger.info("Clearing database...")
    try:
        await session.execute(text('TRUNCATE TABLE "user_profiles" CASCADE'))
        await session.execute(text('TRUNCATE TABLE "users" CASCADE'))
        await session.execute(text('TRUNCATE TABLE "roles" CASCADE'))
        await session.commit()
        logger.info("Database cleared successfully!")
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to clear database: {e}")
        raise


async def main() -> None:
    async for session in get_async_session():
        await clear_db(session)


if __name__ == "__main__":
    asyncio.run(main())
