import pytest

from sqlalchemy import select

from src.db.models.team import Team, TeamCreate


@pytest.mark.asyncio
async def test_async_db_team_creatable_no_migs(db_no_migs, db_session):
    tc = TeamCreate(name='Knuckleheads', city='Rain city', sport='Hockey')
    team = Team(**tc.dict())
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    assert team.id


@pytest.mark.asyncio
async def test_async_db_team_creatable(db, db_session):
    tc = TeamCreate(name='Knuckleheads', city='Rain city', sport='Hockey')
    team = Team(**tc.dict())
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    assert team.id


@pytest.mark.asyncio
async def test_async_db_select_teams(teams, db_session):
    teams.sort(key=lambda t: t.id)
    result = await db_session.execute(select(Team).order_by(Team.id))
    teams_db = result.scalars().all()
    assert teams_db == teams
