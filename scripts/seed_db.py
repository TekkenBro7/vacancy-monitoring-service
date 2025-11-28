import asyncio

from faker import Faker

from scripts.clean_db import clear_db
from src.core.logger import logger
from src.database.session import get_async_session
from src.models.bookmarks import Bookmark
from src.models.comments import Comment
from src.models.companies import Company, Vacancy
from src.models.comparisons import Comparison, ComparisonVacancy
from src.models.currency import Currency
from src.models.locations import City, Country
from src.models.notifications import Notification, NotificationType
from src.models.search import SearchQuery
from src.models.skills import Skill, UserSkill, VacancySkill
from src.models.sources import Source, SourceType
from src.models.subscriptions import (
    Subscription,
    SubscriptionTarget,
    SubscriptionType,
)
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
                phone=fake.phone_number(),
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
            {"name": "RUB", "symbol": "₽"},
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
                "name": "LinkedIn",
                "source_url": "https://linkedin.com",
                "source_type_id": source_type_objs[1].id,
            },
            {
                "name": "Company Career Page",
                "source_url": fake.url(),
                "source_type_id": source_type_objs[2].id,
            },
        ]
        source_objs = [Source(**s) for s in source_data]
        session.add_all(source_objs)
        await session.commit()
        for s in source_objs:
            await session.refresh(s)
        logger.info(f"Inserted {len(source_objs)} sources")

        subscription_targets_data = [
            {"name": "vacancy"},
            {"name": "company"},
            {"name": "category"},
        ]
        target_objs = [SubscriptionTarget(**d) for d in subscription_targets_data]
        session.add_all(target_objs)
        await session.commit()
        for t in target_objs:
            await session.refresh(t)
        logger.info(f"Inserted {len(target_objs)} subscription targets")

        subscription_types_data = [
            {"name": "email", "description": "Email notifications"},
            {"name": "telegram", "description": "Telegram notifications"},
            {"name": "browser", "description": "Browser push notifications"},
        ]
        sub_type_objs = [SubscriptionType(**d) for d in subscription_types_data]
        session.add_all(sub_type_objs)
        await session.commit()
        for sub_types in sub_type_objs:
            await session.refresh(sub_types)
        logger.info(f"Inserted {len(sub_type_objs)} subscription types")

        subscriptions = []
        for user in users:
            for _ in range(fake.random_int(min=1, max=3)):
                subscription = Subscription(
                    user_id=user.id,
                    subscription_type_id=fake.random_element(sub_type_objs).id,
                    target_type_id=fake.random_element(target_objs).id,
                )
                subscriptions.append(subscription)
        session.add_all(subscriptions)
        await session.commit()
        logger.info(f"Inserted {len(subscriptions)} subscriptions")

        queries = []
        for user in users:
            for _ in range(fake.random_int(min=1, max=5)):
                queries.append(
                    SearchQuery(
                        user_id=user.id,
                        query_text=fake.sentence(nb_words=5),
                    )
                )
        session.add_all(queries)
        await session.commit()
        logger.info(f"Inserted {len(queries)} search queries")

        notification_type_data = [
            {"name": "info", "description": "General info message"},
            {"name": "warning", "description": "Important warnings"},
            {"name": "subscription_update", "description": "Subscription activity"},
        ]
        notif_type_objs = [NotificationType(**d) for d in notification_type_data]
        session.add_all(notif_type_objs)
        await session.commit()
        for nt in notif_type_objs:
            await session.refresh(nt)
        logger.info(f"Inserted {len(notif_type_objs)} notification types")

        notifications = []
        for user in users:
            for _ in range(fake.random_int(min=1, max=5)):
                notifications.append(
                    Notification(
                        user_id=user.id,
                        notification_type_id=fake.random_element(notif_type_objs).id,
                        message=fake.sentence(),
                        subscription_id=(
                            fake.random_element(subscriptions).id
                            if subscriptions and fake.boolean()
                            else None
                        ),
                        is_read=fake.boolean(),
                    )
                )
        session.add_all(notifications)
        await session.commit()
        logger.info(f"Inserted {len(notifications)} notifications")

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

        user_skill_links = []
        for user in users:
            user_skills = fake.random_elements(
                skill_objs, length=fake.random_int(1, 5), unique=True
            )
            for sk in user_skills:
                user_skill_links.append(UserSkill(user_id=user.id, skill_id=sk.id))

        session.add_all(user_skill_links)
        await session.commit()
        logger.info(f"Inserted {len(user_skill_links)} user skills")

        country_names = ["USA", "Germany", "Russia", "France"]
        country_objs = [Country(name=c) for c in country_names]
        session.add_all(country_objs)
        await session.commit()
        for country_obj in country_objs:
            await session.refresh(country_obj)
        logger.info(f"Inserted {len(country_objs)} countries")

        city_objs = []
        for country in country_objs:
            for _ in range(fake.random_int(2, 5)):
                city_objs.append(
                    City(
                        name=fake.city(),
                        description=fake.text(50),
                        country_id=country.id,
                    )
                )

        session.add_all(city_objs)
        await session.commit()
        logger.info(f"Inserted {len(city_objs)} cities")

        company_objs = []
        for _ in range(10):
            company_objs.append(
                Company(
                    name=fake.company(),
                    description=fake.text(120),
                    website=fake.url(),
                )
            )
        session.add_all(company_objs)
        await session.commit()
        for company_obj in company_objs:
            await session.refresh(company_obj)
        logger.info(f"Inserted {len(company_objs)} companies")

        vacancy_objs = []
        for _ in range(20):
            vacancy = Vacancy(
                title=fake.job(),
                description=fake.text(200),
                salary_from=fake.random_int(300, 2000) * 10,
                salary_to=fake.random_int(2000, 5000) * 10,
                currency_id=fake.random_element(currency_objs).id,
                company_id=fake.random_element(company_objs).id,
                source_id=fake.random_element(source_objs).id,
                location_id=fake.random_element(city_objs).id,
                vacancy_url=fake.url(),
                is_remote=fake.boolean(),
                is_active=True,
                published_at=fake.date_time(),
            )
            vacancy_objs.append(vacancy)

        session.add_all(vacancy_objs)
        await session.commit()
        for v in vacancy_objs:
            await session.refresh(v)
        logger.info(f"Inserted {len(vacancy_objs)} vacancies")

        vacancy_skill_links = []
        for vacancy in vacancy_objs:
            vskills = fake.random_elements(skill_objs, length=fake.random_int(1, 6), unique=True)
            for sk in vskills:
                vacancy_skill_links.append(VacancySkill(vacancy_id=vacancy.id, skill_id=sk.id))

        session.add_all(vacancy_skill_links)
        await session.commit()
        logger.info(f"Inserted {len(vacancy_skill_links)} vacancy skills")

        comparison_objs = []
        for user in users:
            for _ in range(fake.random_int(1, 3)):
                comparison = Comparison(user_id=user.id, name=fake.sentence(nb_words=3))
                comparison_objs.append(comparison)

        session.add_all(comparison_objs)
        await session.commit()
        for comparison_obj in comparison_objs:
            await session.refresh(comparison_obj)
        logger.info(f"Inserted {len(comparison_objs)} comparisons")

        comparison_vacancy_links = []
        for comparison in comparison_objs:
            linked_vacancies = fake.random_elements(
                vacancy_objs, length=fake.random_int(1, 3), unique=True
            )
            for vac in linked_vacancies:
                comparison_vacancy_links.append(
                    ComparisonVacancy(comparison_id=comparison.id, vacancy_id=vac.id)
                )

        session.add_all(comparison_vacancy_links)
        await session.commit()
        logger.info(f"Inserted {len(comparison_vacancy_links)} comparison-vacancy links")

        comment_objs = []
        for vacancy in vacancy_objs:
            comment_users = fake.random_elements(users, length=fake.random_int(1, 5), unique=True)
            for u in comment_users:
                comment_objs.append(
                    Comment(
                        user_id=u.id,
                        vacancy_id=vacancy.id,
                        content=fake.text(100),
                        rating=fake.random_int(1, 5),
                    )
                )

        session.add_all(comment_objs)
        await session.commit()
        logger.info(f"Inserted {len(comment_objs)} comments")

        bookmark_objs = []
        for user in users:
            bookmarked_vacancies = fake.random_elements(
                vacancy_objs, length=fake.random_int(1, 5), unique=True
            )
            for vac in bookmarked_vacancies:
                bookmark_objs.append(Bookmark(user_id=user.id, vacancy_id=vac.id))

        session.add_all(bookmark_objs)
        await session.commit()
        logger.info(f"Inserted {len(bookmark_objs)} bookmarks")

    logger.info("Seeding database finished!")


if __name__ == "__main__":
    asyncio.run(seed_db())
