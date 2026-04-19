from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.analytics_repository import AnalyticsRepository
from src.models.bookmarks import Bookmark
from src.models.comments import Comment
from src.models.companies import Company, Vacancy
from src.models.currencies import Currency
from src.models.locations import City
from src.models.skills import Skill
from src.models.sources import Source, SourceParseTask, SourceType
from src.models.users import Role, User


@pytest.fixture
def repo(db_session: AsyncSession) -> AnalyticsRepository:
    return AnalyticsRepository(db_session)


@pytest_asyncio.fixture
async def role(db_session: AsyncSession) -> Role:
    role = Role(name="user")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def admin_role(db_session: AsyncSession) -> Role:
    role = Role(name="admin")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def user(role: Role, db_session: AsyncSession) -> User:
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hash",
        role_id=role.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def source_type(db_session: AsyncSession) -> SourceType:
    source_type = SourceType(type_name="API", description="Job board API")
    db_session.add(source_type)
    await db_session.commit()
    await db_session.refresh(source_type)
    return source_type


@pytest_asyncio.fixture
async def source(source_type: SourceType, db_session: AsyncSession) -> Source:
    source = Source(
        name="HeadHunter",
        source_url="https://hh.ru",
        source_type_id=source_type.id,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def currency(db_session: AsyncSession) -> Currency:
    currency = Currency(name="RUB", symbol="₽")
    db_session.add(currency)
    await db_session.commit()
    await db_session.refresh(currency)
    return currency


@pytest_asyncio.fixture
async def company(db_session: AsyncSession) -> Company:
    company = Company(name="Test Company", description="Test description")
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def city(db_session: AsyncSession) -> City:
    city = City(name="Moscow")
    db_session.add(city)
    await db_session.commit()
    await db_session.refresh(city)
    return city


@pytest_asyncio.fixture
async def skill(db_session: AsyncSession) -> Skill:
    skill = Skill(name="Python")
    db_session.add(skill)
    await db_session.commit()
    await db_session.refresh(skill)
    return skill


@pytest_asyncio.fixture
async def vacancy(
    source: Source,
    company: Company,
    city: City,
    currency: Currency,
    db_session: AsyncSession,
) -> Vacancy:
    vacancy = Vacancy(
        title="Python Developer",
        description="Test vacancy",
        external_id="ext_1",
        source_id=source.id,
        company_id=company.id,
        location_id=city.id,
        currency_id=currency.id,
        salary_from=100000,
        salary_to=150000,
        is_active=True,
        is_remote=True,
        internship=False,
        fingerprint="fp_1",
    )
    db_session.add(vacancy)
    await db_session.commit()
    await db_session.refresh(vacancy)
    return vacancy


class TestGetVacancyCounts:
    @pytest.mark.asyncio
    async def test_returns_zeros_when_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_vacancy_counts()

        assert result == {
            "total": 0,
            "active": 0,
            "with_salary": 0,
            "remote": 0,
            "internship": 0,
        }

    @pytest.mark.asyncio
    async def test_counts_vacancies_correctly(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancies = [
            Vacancy(
                title="V1",
                external_id="1",
                source_id=source.id,
                company_id=company.id,
                is_active=True,
                is_remote=True,
                internship=False,
                salary_from=100000,
                fingerprint="fp1",
            ),
            Vacancy(
                title="V2",
                external_id="2",
                source_id=source.id,
                company_id=company.id,
                is_active=True,
                is_remote=False,
                internship=True,
                salary_to=80000,
                fingerprint="fp2",
            ),
            Vacancy(
                title="V3",
                external_id="3",
                source_id=source.id,
                company_id=company.id,
                is_active=False,
                is_remote=True,
                internship=False,
                fingerprint="fp3",
            ),
        ]
        for v in vacancies:
            db_session.add(v)
        await db_session.commit()

        result = await repo.get_vacancy_counts()

        assert result["total"] == 3
        assert result["active"] == 2
        assert result["with_salary"] == 2
        assert result["remote"] == 2
        assert result["internship"] == 1


class TestCountMethods:
    @pytest.mark.asyncio
    async def test_count_users_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_users()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_users(self, repo: AnalyticsRepository, user: User) -> None:
        result = await repo.count_users()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_companies_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_companies()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_companies(self, repo: AnalyticsRepository, company: Company) -> None:
        result = await repo.count_companies()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_skills_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_skills()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_skills(self, repo: AnalyticsRepository, skill: Skill) -> None:
        result = await repo.count_skills()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_sources_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_sources()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_sources(self, repo: AnalyticsRepository, source: Source) -> None:
        result = await repo.count_sources()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_bookmarks_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_bookmarks()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_bookmarks(
        self, repo: AnalyticsRepository, user: User, vacancy: Vacancy, db_session: AsyncSession
    ) -> None:
        bookmark = Bookmark(user_id=user.id, vacancy_id=vacancy.id)
        db_session.add(bookmark)
        await db_session.commit()

        result = await repo.count_bookmarks()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_comments_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_comments()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_comments(
        self, repo: AnalyticsRepository, user: User, vacancy: Vacancy, db_session: AsyncSession
    ) -> None:
        comment = Comment(user_id=user.id, vacancy_id=vacancy.id, content="Test", rating=5)
        db_session.add(comment)
        await db_session.commit()

        result = await repo.count_comments()
        assert result == 1


class TestCountInPeriod:
    @pytest.mark.asyncio
    async def test_count_vacancies_in_period_empty(self, repo: AnalyticsRepository) -> None:
        now = datetime.now(UTC)
        result = await repo.count_vacancies_in_period(now - timedelta(days=7), now)
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_vacancies_in_period(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        now = datetime.now(UTC)
        result = await repo.count_vacancies_in_period(
            now - timedelta(days=1), now + timedelta(days=1)
        )
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_vacancies_in_period_excludes_outside(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        now = datetime.now(UTC)
        result = await repo.count_vacancies_in_period(
            now - timedelta(days=10), now - timedelta(days=5)
        )
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_users_in_period(self, repo: AnalyticsRepository, user: User) -> None:
        now = datetime.now(UTC)
        result = await repo.count_users_in_period(now - timedelta(days=1), now + timedelta(days=1))
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_companies_in_period(
        self, repo: AnalyticsRepository, company: Company
    ) -> None:
        now = datetime.now(UTC)
        result = await repo.count_companies_in_period(
            now - timedelta(days=1), now + timedelta(days=1)
        )
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_bookmarks_in_period(
        self, repo: AnalyticsRepository, user: User, vacancy: Vacancy, db_session: AsyncSession
    ) -> None:
        bookmark = Bookmark(user_id=user.id, vacancy_id=vacancy.id)
        db_session.add(bookmark)
        await db_session.commit()

        now = datetime.now(UTC)
        result = await repo.count_bookmarks_in_period(
            now - timedelta(days=1), now + timedelta(days=1)
        )
        assert result == 1


class TestGetVacanciesByDate:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_vacancies(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_vacancies_by_date(datetime.now(UTC) - timedelta(days=7))
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_vacancies_grouped_by_date(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.get_vacancies_by_date(datetime.now(UTC) - timedelta(days=1))
        assert len(result) == 1
        assert result[0][1] == 1


class TestGetSalaries:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_vacancies(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_salaries()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_salaries(self, repo: AnalyticsRepository, vacancy: Vacancy) -> None:
        result = await repo.get_salaries()
        assert len(result) == 1
        assert result[0] == (100000, 150000)

    @pytest.mark.asyncio
    async def test_filters_by_currency(
        self,
        repo: AnalyticsRepository,
        vacancy: Vacancy,
        currency: Currency,
    ) -> None:
        result = await repo.get_salaries(currency_id=currency.id)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_excludes_other_currency(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.get_salaries(currency_id=99999)
        assert result == []


class TestCountVacanciesWithoutSalary:
    @pytest.mark.asyncio
    async def test_returns_zero_when_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_vacancies_without_salary()
        assert result == 0

    @pytest.mark.asyncio
    async def test_counts_vacancies_without_salary(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="No salary",
            external_id="no_sal",
            source_id=source.id,
            company_id=company.id,
            fingerprint="fp_no_sal",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.count_vacancies_without_salary()
        assert result == 1

    @pytest.mark.asyncio
    async def test_excludes_vacancies_with_salary(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.count_vacancies_without_salary()
        assert result == 0


class TestGetTopCompaniesRaw:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_data(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_top_companies_raw()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_companies_with_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy, company: Company
    ) -> None:
        result = await repo.get_top_companies_raw()
        assert len(result) == 1
        assert result[0].id == company.id
        assert result[0].vacancy_count == 1

    @pytest.mark.asyncio
    async def test_respects_limit(
        self,
        repo: AnalyticsRepository,
        source: Source,
        db_session: AsyncSession,
    ) -> None:
        for i in range(5):
            company = Company(name=f"Company {i}")
            db_session.add(company)
            await db_session.flush()

            vacancy = Vacancy(
                title=f"Vacancy {i}",
                external_id=f"ext_{i}",
                source_id=source.id,
                company_id=company.id,
                is_active=True,
                fingerprint=f"fp_{i}",
            )
            db_session.add(vacancy)

        await db_session.commit()

        result = await repo.get_top_companies_raw(limit=3)
        assert len(result) == 3


class TestGetActiveVacanciesCount:
    @pytest.mark.asyncio
    async def test_returns_one_when_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_active_vacancies_count()
        assert result == 1

    @pytest.mark.asyncio
    async def test_counts_active_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.get_active_vacancies_count()
        assert result == 1

    @pytest.mark.asyncio
    async def test_excludes_inactive(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Inactive",
            external_id="inactive",
            source_id=source.id,
            company_id=company.id,
            is_active=False,
            fingerprint="fp_inactive",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.get_active_vacancies_count()
        assert result == 1


class TestGetTopSkillsRaw:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_data(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_top_skills_raw()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_skills_with_vacancies(
        self,
        repo: AnalyticsRepository,
        vacancy: Vacancy,
        skill: Skill,
        db_session: AsyncSession,
    ) -> None:
        await db_session.refresh(vacancy, ["skills"])
        vacancy.skills.append(skill)
        await db_session.commit()

        result = await repo.get_top_skills_raw()
        assert len(result) == 1
        assert result[0].id == skill.id
        assert result[0].vacancy_count == 1


class TestGetTopCitiesRaw:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_data(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_top_cities_raw()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_cities_with_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy, city: City
    ) -> None:
        result = await repo.get_top_cities_raw()
        assert len(result) == 1
        assert result[0].id == city.id
        assert result[0].vacancy_count == 1


class TestGetSourcesStatsRaw:
    @pytest.mark.asyncio
    async def test_returns_sources(
        self, repo: AnalyticsRepository, source: Source, source_type: SourceType
    ) -> None:
        result = await repo.get_sources_stats_raw()
        assert len(result) == 1
        assert result[0].id == source.id
        assert result[0].type_name == source_type.type_name

    @pytest.mark.asyncio
    async def test_counts_vacancies_per_source(
        self, repo: AnalyticsRepository, vacancy: Vacancy, source: Source
    ) -> None:
        result = await repo.get_sources_stats_raw()
        assert result[0].vacancy_count == 1


class TestGetSourceParsingStatsRaw:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_tasks(
        self, repo: AnalyticsRepository, source: Source
    ) -> None:
        result = await repo.get_source_parsing_stats_raw(datetime.now(UTC) - timedelta(days=7))
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_parsing_stats(
        self, repo: AnalyticsRepository, source: Source, db_session: AsyncSession
    ) -> None:
        task = SourceParseTask(
            source_id=source.id,
            parse_date=datetime.now(UTC).date(),
            status="completed",
            attempts=1,
        )
        db_session.add(task)
        await db_session.commit()

        result = await repo.get_source_parsing_stats_raw(datetime.now(UTC) - timedelta(days=1))
        assert len(result) == 1
        assert result[0].id == source.id
        assert result[0].success == 1


class TestUserStats:
    @pytest.mark.asyncio
    async def test_count_users_since(self, repo: AnalyticsRepository, user: User) -> None:
        result = await repo.count_users_since(datetime.now(UTC) - timedelta(days=1))
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_users_since_excludes_old(
        self, repo: AnalyticsRepository, user: User
    ) -> None:
        result = await repo.count_users_since(datetime.now(UTC) + timedelta(days=1))
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_users_with_bookmarks_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_users_with_bookmarks()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_users_with_bookmarks(
        self, repo: AnalyticsRepository, user: User, vacancy: Vacancy, db_session: AsyncSession
    ) -> None:
        bookmark = Bookmark(user_id=user.id, vacancy_id=vacancy.id)
        db_session.add(bookmark)
        await db_session.commit()

        result = await repo.count_users_with_bookmarks()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_users_with_skills_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_users_with_skills()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_users_with_skills(
        self, repo: AnalyticsRepository, user: User, skill: Skill, db_session: AsyncSession
    ) -> None:
        user.skills.append(skill)
        await db_session.commit()

        result = await repo.count_users_with_skills()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_total_user_skills(
        self, repo: AnalyticsRepository, user: User, skill: Skill, db_session: AsyncSession
    ) -> None:
        user.skills.append(skill)
        await db_session.commit()

        result = await repo.count_total_user_skills()
        assert result == 1


class TestGetUsersByDate:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_users(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_users_by_date(datetime.now(UTC) - timedelta(days=7))
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_users_grouped_by_date(
        self, repo: AnalyticsRepository, user: User
    ) -> None:
        result = await repo.get_users_by_date(datetime.now(UTC) - timedelta(days=1))
        assert len(result) == 1
        assert result[0][1] == 1


class TestGetUsersByRoleRaw:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_users(self, repo: AnalyticsRepository, role: Role) -> None:
        result = await repo.get_users_by_role_raw()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_users_by_role(
        self, repo: AnalyticsRepository, user: User, role: Role
    ) -> None:
        result = await repo.get_users_by_role_raw()
        assert len(result) == 1
        assert result[0].id == role.id
        assert result[0].cnt == 1


class TestVacancyStatsRaw:
    @pytest.mark.asyncio
    async def test_get_experience_stats_raw_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_experience_stats_raw()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_experience_stats_raw(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Test",
            external_id="exp_test",
            source_id=source.id,
            company_id=company.id,
            is_active=True,
            experience="3-5 лет",
            fingerprint="fp_exp",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.get_experience_stats_raw()
        assert len(result) == 1
        assert result[0].experience == "3-5 лет"
        assert result[0].cnt == 1

    @pytest.mark.asyncio
    async def test_get_employment_stats_raw(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Test",
            external_id="emp_test",
            source_id=source.id,
            company_id=company.id,
            is_active=True,
            employment="Полная занятость",
            fingerprint="fp_emp",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.get_employment_stats_raw()
        assert len(result) == 1
        assert result[0].employment == "Полная занятость"

    @pytest.mark.asyncio
    async def test_get_schedule_stats_raw(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Test",
            external_id="sch_test",
            source_id=source.id,
            company_id=company.id,
            is_active=True,
            schedule="Удалённая работа",
            fingerprint="fp_sch",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.get_schedule_stats_raw()
        assert len(result) == 1
        assert result[0].schedule == "Удалённая работа"


class TestCountActiveVacancies:
    @pytest.mark.asyncio
    async def test_count_remote_active_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.count_remote_active_vacancies()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_remote_excludes_inactive(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Test",
            external_id="rem_inact",
            source_id=source.id,
            company_id=company.id,
            is_active=False,
            is_remote=True,
            fingerprint="fp_rem_inact",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.count_remote_active_vacancies()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_internship_active_vacancies_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_internship_active_vacancies()
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_internship_active_vacancies(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="Internship",
            external_id="intern",
            source_id=source.id,
            company_id=company.id,
            is_active=True,
            internship=True,
            fingerprint="fp_intern",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.count_internship_active_vacancies()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_active_vacancies_with_salary(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.count_active_vacancies_with_salary()
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_active_vacancies_with_salary_excludes_no_salary(
        self,
        repo: AnalyticsRepository,
        source: Source,
        company: Company,
        db_session: AsyncSession,
    ) -> None:
        vacancy = Vacancy(
            title="No Salary",
            external_id="no_sal_active",
            source_id=source.id,
            company_id=company.id,
            is_active=True,
            fingerprint="fp_no_sal_active",
        )
        db_session.add(vacancy)
        await db_session.commit()

        result = await repo.count_active_vacancies_with_salary()
        assert result == 0


class TestCountVacanciesSince:
    @pytest.mark.asyncio
    async def test_returns_zero_when_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.count_vacancies_since(datetime.now(UTC) - timedelta(days=7))
        assert result == 0

    @pytest.mark.asyncio
    async def test_counts_recent_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.count_vacancies_since(datetime.now(UTC) - timedelta(days=1))
        assert result == 1

    @pytest.mark.asyncio
    async def test_excludes_old_vacancies(
        self, repo: AnalyticsRepository, vacancy: Vacancy
    ) -> None:
        result = await repo.count_vacancies_since(datetime.now(UTC) + timedelta(days=1))
        assert result == 0


class TestGetTotalVacanciesCount:
    @pytest.mark.asyncio
    async def test_returns_one_when_empty(self, repo: AnalyticsRepository) -> None:
        result = await repo.get_total_vacancies_count()
        assert result == 1

    @pytest.mark.asyncio
    async def test_counts_all_vacancies(self, repo: AnalyticsRepository, vacancy: Vacancy) -> None:
        result = await repo.get_total_vacancies_count()
        assert result == 1
