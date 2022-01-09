from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from src.db.db import create_async_db_engine, get_session_with_engine, init_db_with_engine, reset_db_with_engine
from src.db.models import Team, TeamCreate
from src.main import app as fastapi_app, get_session

# Testing Sqlite async
TEST_DB_NAME = 'willtheywinfastapi-test.db'
TEST_DATABASE_URL = f'sqlite+aiosqlite:///{TEST_DB_NAME}'

engine = create_async_db_engine(TEST_DATABASE_URL)


def pytest_report_header(config):
    return ["PROJECT: willtheywin-fast", ]


@pytest.fixture
def app():
    return fastapi_app


# -- Client fixtures --

@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url='http://') as client:
        yield client


# -- DB fixtures --

async def override_get_session():
    db = None
    try:
        db = get_session_with_engine(engine)
        yield db
    finally:
        if db:
            await db.close()


@pytest.fixture(scope='session', autouse=True)
def override_get_session_fixture():
    fastapi_app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def db():
    path = Path.cwd().joinpath(TEST_DB_NAME)  # cwd is the directory pytest is invoked from
    assert path.exists() is False

    config = Config('alembic.ini')
    config.set_main_option('sqlalchemy.url', TEST_DATABASE_URL)
    command.upgrade(config, 'head')

    yield

    assert path.exists()
    path.unlink()
    assert path.exists() is False


@pytest.fixture
async def db_no_migs():
    path = Path.cwd().joinpath(TEST_DB_NAME)  # cwd is the directory pytest is invoked from
    assert path.exists() is False

    await init_db_with_engine(engine)

    yield

    await reset_db_with_engine(engine)

    assert path.exists() is True
    path.unlink()
    assert path.exists() is False


@pytest.fixture
async def db_session():
    session = get_session_with_engine(engine)
    yield session
    await session.close()


# --  Model fixtures --

@pytest.fixture
async def team(db, db_session):
    # Use TeamCreate for field normalization on name, city and sport but Team for the db query.
    tc = TeamCreate(name='Knuckleheads', city='Rain city', sport='Hockey')
    team = Team(**tc.dict())
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def teams(db, db_session):
    # Use TeamCreate for field normalization on name, city and sport but Team for the db query.
    teams = [
        TeamCreate(name='Knuckleheads', city='Rain city', sport='Hockey'),
        TeamCreate(name='Flames', city='Cow town', sport='Hockey'),
        TeamCreate(name='Blue Jays', city='Taranta', sport='Baseball'),
    ]

    for i, tc in enumerate(teams):
        team = Team(**tc.dict())
        teams[i] = team
        db_session.add(team)

    await db_session.commit()

    for t in teams:
        await db_session.refresh(t)

    return teams
