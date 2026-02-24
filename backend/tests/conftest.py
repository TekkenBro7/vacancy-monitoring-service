from collections.abc import AsyncGenerator, Callable, Generator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import postgres_config
from src.database.base import Base
from src.database.session import get_async_session
from src.main import app


@pytest_asyncio.fixture()
async def test_async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates and deliver an asynchronous engine for the entire test session
    """
    engine = create_async_engine(postgres_config.async_test_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(test_async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new asynchronous SQLAlchemy session for each test with transaction isolation
    """
    session_maker = async_sessionmaker(
        test_async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture  # type: ignore
def override_get_db(
    db_session: AsyncSession,
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture  # type: ignore
def overridden_app(
    override_get_db: Callable[[], AsyncGenerator[AsyncSession, None]],
) -> Generator[FastAPI, None, None]:
    app.dependency_overrides[get_async_session] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(overridden_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=overridden_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
