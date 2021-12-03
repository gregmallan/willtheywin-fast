from typing import Dict, List

import pytest

from src.db.models import Team


def not_found_response_json(team_id):
    return {'detail': f'No team found with id={team_id}'}


@pytest.mark.asyncio
class TestGetTeam():

    async def test_no_teams(self, async_client, db):
        non_existent_id = 1
        response = await async_client.get(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_team_exist_invalid_id(self, async_client, team):
        invalid_id = team.name
        response = await async_client.get(f'/teams/{invalid_id}')
        assert response.status_code == 422
        res_data = response.json()
        assert 'team_id' in res_data['detail'][0]['loc']

    async def test_single_team_exist_not_found(self, async_client, team):
        non_existent_id = team.id + 1
        response = await async_client.get(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_single_team_exist_found(self, async_client, team):
        response = await async_client.get(f'/teams/{team.id}')
        assert response.status_code == 200
        assert response.json() == team

    async def test_multiple_teams_exist_not_found(self, async_client, teams):
        sort_team_objs_by_id(teams)
        non_existent_id = teams[-1].id + 1
        response = await async_client.get(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_multiple_teams_found(self, async_client, teams):
        for team in teams:
            response = await async_client.get(f'/teams/{team.id}')
            assert response.status_code == 200
            assert response.json() == team


def sort_team_objs_by_id(teams: List[Team]):
    teams.sort(key=lambda t: t.id)


def sort_team_dicts_by_id(teams: List[Dict]):
    teams.sort(key=lambda t: t['id'])


@pytest.mark.asyncio
class TestGetTeams:

    async def test_get_teams_none_exist(self, async_client, db):
        response = await async_client.get('/teams')
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_teams(self, async_client, teams):
        response = await async_client.get('/teams')
        assert response.status_code == 200
        response_teams = response.json()
        assert response_teams

        sort_team_dicts_by_id(response_teams)
        sort_team_objs_by_id(teams)

        # TODO: Why does pytest say list of dicts == list of Team objects. Not using only this assertion until I know why.
        #  I think it may come from SQLModel <- pydantic BaseModel <- ModelMetaclass. See test_model_eq.py
        assert response.json() == teams

        for team_dict, team in zip(response_teams, teams):
            assert team_dict == team
            assert team_dict == team.dict()
