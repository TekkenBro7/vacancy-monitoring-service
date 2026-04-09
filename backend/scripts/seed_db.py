import asyncio

from faker import Faker

from scripts.clean_db import clear_db
from src.core.logger import logger
from src.database.session import get_async_session
from src.models.currencies import Currency
from src.models.locations import City
from src.models.secondary_tables import (
    user_skills_table,
)
from src.models.skills import Skill
from src.models.sources import Source, SourceType
from src.models.users import Role, User, UserProfile

fake = Faker()


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
                phone=fake.msisdn(),
                avatar_url=fake.image_url(),
                desired_position=fake.job(),
                desired_salary=fake.random_int(min=500, max=5000) * 10,
                desired_salary_currency_id=None,
            )
            profiles.append(profile)
        session.add_all(profiles)
        await session.commit()
        logger.info(f"Inserted {len(profiles)} user profiles")

        currency_data = [
            {"name": "USD", "symbol": "$"},
            {"name": "EUR", "symbol": "€"},
            {"name": "RUR", "symbol": "₽"},
            {"name": "BYR", "symbol": "Br"},
            {"name": "UAH", "symbol": "₴"},
            {"name": "KZT", "symbol": "₸"},
            {"name": "GBP", "symbol": "£"},
            {"name": "UZS", "symbol": "сўм"},
            {"name": "KGS", "symbol": "С"},
            {"name": "AZN", "symbol": "₼"},
        ]
        currency_objs = [Currency(**c) for c in currency_data]
        session.add_all(currency_objs)
        await session.commit()
        for c in currency_objs:
            await session.refresh(c)
        logger.info(f"Inserted {len(currency_objs)} currencies")

        for profile in profiles:
            profile.desired_salary_currency_id = fake.random_element(currency_objs).id
        await session.commit()

        source_types_data = [
            {"type_name": "job_board", "description": "Vacancy aggregator"},
            {"type_name": "social_network", "description": "Social media platform"},
            {"type_name": "company_site", "description": "Official company website"},
        ]
        source_type_objs = [SourceType(**d) for d in source_types_data]
        session.add_all(source_type_objs)
        await session.commit()
        for st in source_type_objs:
            await session.refresh(st)
        logger.info(f"Inserted {len(source_type_objs)} source types")

        source_data = [
            {
                "name": "HeadHunter",
                "source_url": "https://hh.ru",
                "source_type_id": source_type_objs[0].id,
            },
            {
                "name": "SuperJob",
                "source_url": "https://www.superjob.ru",
                "source_type_id": source_type_objs[0].id,
            },
            {
                "name": "PracaBy",
                "source_url": "https://praca.by",
                "source_type_id": source_type_objs[0].id,
            },
            {
                "name": "EPAM",
                "source_url": "https://careers.epam.com",
                "source_type_id": source_type_objs[2].id,
            },
        ]
        source_objs = [Source(**s) for s in source_data]
        session.add_all(source_objs)
        await session.commit()
        for s in source_objs:
            await session.refresh(s)
        logger.info(f"Inserted {len(source_objs)} sources")

        skill_names = [
            "Python",
            "FastAPI",
            "SQL",
            "Docker",
            "Kubernetes",
            "Linux",
            "JavaScript",
            "React",
            "AI",
            "ML",
            "Git",
            "PostgreSQL",
        ]
        skill_objs = [Skill(name=s) for s in skill_names]
        session.add_all(skill_objs)
        await session.commit()
        for skill_obj in skill_objs:
            await session.refresh(skill_obj)
        logger.info(f"Inserted {len(skill_objs)} skills")

        total_user_skill_links = 0
        for user in users:
            user_skills = fake.random_elements(
                skill_objs, length=fake.random_int(1, 5), unique=True
            )
            for sk in user_skills:
                await session.execute(
                    user_skills_table.insert().values(user_id=user.id, skill_id=sk.id)
                )
                total_user_skill_links += 1

        await session.commit()
        logger.info(f"Inserted {total_user_skill_links} user skills")

        city_objs = [
            City(name="Минск"),
            City(name="Москва"),
            City(name="Санкт-Петербург"),
        ]

        session.add_all(city_objs)
        await session.commit()
        logger.info(f"Inserted {len(city_objs)} cities")

    logger.info("Seeding database finished!")


if __name__ == "__main__":
    asyncio.run(seed_db())
