import pytest
from sqlmodel import select

from src.db.models.sport import Sport, SportCreate
from src.db.models.team import Team, TeamCreate


@pytest.mark.asyncio
async def test_async_db_team_creatable_no_migs(db_no_migs, db_session, hockey):
    tc = TeamCreate(name='Knuckleheads', city='Rain city')
    team = Team(**tc.dict(), sport=hockey)
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    assert team.id
    assert team.sport_id == hockey.id
    assert team.sport == hockey


@pytest.mark.asyncio
async def test_async_db_team_creatable(db, db_session, hockey):
    tc = TeamCreate(name='Knuckleheads', city='Rain city')
    team = Team(**tc.dict(), sport=hockey)
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    assert team.id
    assert team.sport_id == hockey.id
    assert team.sport == hockey


@pytest.mark.asyncio
async def test_async_db_team_sport(db, db_session, hockey):
    tc = TeamCreate(name='Knuckleheads', city='Rain city')
    team = Team(**tc.dict(), sport=hockey)
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    query = select(Team).where(Team.id == team.id)
    result = await db_session.execute(query)
    db_team = result.scalars().one()

    assert db_team
    assert db_team == team
    assert db_team.sport == hockey


@pytest.mark.asyncio
async def test_async_db_select_teams(teams, db_session):
    teams.sort(key=lambda t: t.id)
    result = await db_session.execute(select(Team).order_by(Team.id))
    teams_db = result.scalars().all()
    assert teams_db == teams
