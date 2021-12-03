import pytest

from sqlalchemy import select

from src.db.models import Team


@pytest.mark.asyncio
async def test_async_db_select_teams(teams, db_session):
    teams.sort(key=lambda t: t.id)
    result = await db_session.execute(select(Team).order_by(Team.id))
    teams_db = result.scalars().all()
    assert teams_db == teams
