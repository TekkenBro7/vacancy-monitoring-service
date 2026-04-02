import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.database.session import get_async_session


async def clear_db(session: AsyncSession) -> None:
    logger.info("Clearing database...")

    try:
        await session.execute(
            text(
                """
            TRUNCATE TABLE
                comparison_vacancies,
                comparisons,
                vacancies,
                companies,
                cities,
                vacancy_skills,
                user_skills,
                skills,
                comments,
                bookmarks,
                search_queries,
                subscriptions,
                subscription_types,
                subscription_targets,
                sources,
                source_types,
                notifications,
                notification_types,
                user_profiles,
                users,
                roles,
                currencies
            RESTART IDENTITY CASCADE
            """
            )
        )
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
