from typing import Dict, List

import pytest

from src.db.models import Team


def sort_team_objs_by_id(teams: List[Team]):
    teams.sort(key=lambda t: t.id)


def sort_team_dicts_by_id(teams: List[Dict]):
    teams.sort(key=lambda t: t['id'])


@pytest.mark.asyncio
async def test_get_teams(async_client, teams):
    response = await async_client.get('/teams')
    assert response.status_code == 200
    assert (response.json())

    response_teams = response.json()
    sort_team_dicts_by_id(response_teams)
    sort_team_objs_by_id(teams)

    # TODO: Why does pytest say list of dicts == list of Team objects. Not using only this assertion until I know why.
    #  I think it may come from SQLModel <- pydantic BaseModel <- ModelMetaclass. See test_model_eq.py
    assert response.json() == teams

    for team_dict, team in zip(response_teams, teams):
        assert team_dict == team
        assert team_dict == team.dict()
