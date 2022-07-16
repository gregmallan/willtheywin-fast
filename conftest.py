from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from src.db.db import create_async_db_engine, get_session_with_engine, init_db_with_engine, reset_db_with_engine
from src.db.models.team import Team, TeamCreate
from src.db.models.sport import Sport, SportCreate
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
    # remove if existing from previous test errors
    if path.exists():
        path.unlink()
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
    if path.exists():
        path.unlink()
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

async def create_sport(db_session, name):
    sc = SportCreate(name=name)
    sport = Sport(**sc.dict())
    db_session.add(sport)
    await db_session.commit()
    await db_session.refresh(sport)
    assert sport.id is not None
    return sport


@pytest.fixture
async def hockey(db, db_session):
    return await create_sport(db_session, 'Hockey (NHL)')


@pytest.fixture
async def hockey_with_teams(db, db_session, hockey):
    teams = [
        (TeamCreate(name='Knuckleheads', city='Rain city'), hockey),
        (TeamCreate(name='Flames', city='Cow town'), hockey),
    ]

    for i, team_tup in enumerate(teams):
        team = Team(**team_tup[0].dict(), sport=team_tup[1])
        teams[i] = team
        db_session.add(team)

    await db_session.commit()

    for t in teams:
        await db_session.refresh(t)

    return hockey, teams


@pytest.fixture
async def baseball(db, db_session):
    return await create_sport(db_session, 'Baseball (MLB)')


@pytest.fixture
async def basketball(db, db_session):
    return await create_sport(db_session, 'Basketball (NBA)')


@pytest.fixture
async def football(db, db_session):
    return await create_sport(db_session, 'Football (NFL)')


@pytest.fixture
async def sports(db, db_session):
    # Use SportCreate for field normalization on name but Sport for the db query.
    sports = [
        SportCreate(name='Hockey (NHL)'),
        SportCreate(name='BASEBALL (MLB)'),
        SportCreate(name='basketball (NBA)'),
        SportCreate(name='Football (NFL)'),
    ]

    for i, sport in enumerate(sports):
        sport = Sport(**sport.dict())
        sports[i] = sport
        db_session.add(sport)

    await db_session.commit()

    for s in sports:
        await db_session.refresh(s)

    return sports


@pytest.fixture
async def team(db, db_session, hockey):
    # Use TeamCreate for field normalization on name, city and sport but Team for the db query.
    tc = TeamCreate(name='Knuckleheads', city='Rain city')
    team = Team(**tc.dict(), sport=hockey)
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def teams(db, db_session, hockey, baseball, basketball):
    # Use TeamCreate for field normalization on name, city and sport but Team for the db query.
    teams = [
        (TeamCreate(name='Knuckleheads', city='Rain city'), hockey),
        (TeamCreate(name='Flames', city='Cow town'), hockey),
        (TeamCreate(name='Blue Jays', city='Taranta'), baseball),
        (TeamCreate(name='Raptors', city='Taranta'), basketball),
    ]

    for i, team_tup in enumerate(teams):
        team = Team(**team_tup[0].dict(), sport=team_tup[1])
        teams[i] = team
        db_session.add(team)

    await db_session.commit()

    for t in teams:
        await db_session.refresh(t)

    return teams


@pytest.fixture
async def sports_with_teams(db, db_session, hockey, baseball, basketball, football):
    # Use TeamCreate for field normalization on name, city and sport but Team for the db query.
    teams = [
        (TeamCreate(name='Knuckleheads', city='Rain city'), hockey),
        (TeamCreate(name='Flames', city='Cow town'), hockey),
        (TeamCreate(name='Blue Jays', city='Taranta'), baseball),
        (TeamCreate(name='Raptors', city='Taranta'), basketball),
    ]

    sports = [hockey, baseball, basketball, football]
    sport_teams = {sport.id: [] for sport in sports}

    for i, team_tup in enumerate(teams):
        team = Team(**team_tup[0].dict(), sport=team_tup[1])
        teams[i] = team
        db_session.add(team)

        sport_teams[team_tup[1].id].append(team)

    await db_session.commit()

    for t in teams:
        await db_session.refresh(t)

    return sports, sport_teams
