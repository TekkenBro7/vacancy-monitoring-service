import asyncio

from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.database.session import get_async_session
from src.models.users import Role, User, UserProfile

fake = Faker()


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


async def seed_db() -> None:
    logger.info("Seeding database started")

    async for session in get_async_session():
        await clear_db(session)

        roles = ["admin", "user"]
        role_objs = [Role(name=role) for role in roles]

        session.add_all(role_objs)
        await session.commit()
        for role in role_objs:
            await session.refresh(role)
        logger.info(f"Inserted roles: {roles}")

        users = []
        for i in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                password_hash=fake.password(),
                role_id=role_objs[i % len(role_objs)].id,
            )
            users.append(user)
        session.add_all(users)
        await session.commit()
        logger.info(f"Inserted {len(users)} users")

        profiles = []
        for user in users:
            profile = UserProfile(
                user_id=user.id,
                full_name=fake.name(),
                phone=fake.phone_number(),
                avatar_url=fake.image_url(),
                desired_position=fake.job(),
                desired_salary=fake.random_int(min=500, max=5000) * 10,
            )
            profiles.append(profile)
        session.add_all(profiles)
        await session.commit()
        logger.info(f"Inserted {len(profiles)} user profiles")

    logger.info("Seeding database finished!")


if __name__ == "__main__":
    asyncio.run(seed_db())
