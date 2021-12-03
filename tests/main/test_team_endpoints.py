from typing import Dict, List

import pytest

from src.db.models import Team, TeamCreate


def not_found_response_json(team_id):
    return {'detail': f'No team found with id={team_id}'}


@pytest.mark.asyncio
class TestCreateTeam():

    @pytest.mark.parametrize('team_dict', [
        dict(name='Knuckleheads', city='Rain city', sport='Hockey'),
        dict(name='knuckleheads', city='rain city', sport='hockey'),
        dict(name='KNUCKLEHEADS', city='RAIN CITY', sport='HOCKEY'),
        dict(name='knUCKLEHEaDS', city='RaIn cITY', sport='hocKeY'),
        dict(name='knuckleheads', city='rain  city', sport='hockey'),
    ])
    async def test_create_team_already_exists(self, team_dict, async_client, team):
        response = await async_client.post('/teams', json=team_dict)
        assert response.status_code == 400
        res_data = response.json()
        assert 'IntegrityError' in res_data['detail']
        for k, v in team_dict.items():
            assert k in res_data['detail']
            assert ' '.join(word.strip() for word in v.split(' ') if word).lower() in res_data['detail']

    async def test_create_none_exist(self, async_client, db):
        team_dict = dict(name='Knuckleheads', city='Rain  city', sport='Hockey')
        expected_team_dict = dict(name='knuckleheads', city='rain city', sport='hockey')
        response = await async_client.post('/teams', json=team_dict)
        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == expected_team_dict

    async def test_create_with_existing_teams(self, async_client, teams):
        team_dict = dict(name='Canucks', city='Vancouver', sport='Hockey')
        response = await async_client.post('/teams', json=team_dict)
        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == {k: v.lower() for k, v in team_dict.items()}

    @pytest.mark.parametrize('team_dict', [
        dict(name='Canucks', city='Rain city', sport='Hockey'),
        dict(name='Flames', city='Calgary', sport='Hockey'),
        dict(name='Flames', city='Cow Town', sport='Curling'),
        dict(name='Blue Jays', city='Toronto', sport='Baseball'),
        dict(name='Raptors', city='Toronto', sport='Basketball'),
    ])
    async def test_create_with_similar_teams(self, team_dict, async_client, teams):
        # teams fixture data (excluding id)
        # teams = [
        #     Team(name='Knuckleheads', city='Rain city', sport='Hockey'),
        #     Team(name='Flames', city='Cow town', sport='Hockey'),
        #     Team(name='Blue Jays', city='Taranta', sport='Baseball'),
        # ]

        response = await async_client.post('/teams', json=team_dict)

        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == {k: v.lower() for k, v in team_dict.items()}


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


@pytest.mark.asyncio
class TestUpdateTeam():

    async def test_no_teams(self, async_client, db):
        non_existent_id = 1
        update_data = dict(name='Canucks', city='Rain city', sport='hockey')
        response = await async_client.put(f'/teams/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_teams_not_found(self, async_client, team):
        non_existent_id = team.id + 1
        update_data = dict(name='Canucks', city='Rain city', sport='hockey')
        response = await async_client.put(f'/teams/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    @pytest.mark.parametrize('bad_data', [
        dict(name=None, city='cow town', sport='hockey'),
        dict(name='Flames', city=None, sport='hockey'),
        dict(name='Flames', city='Cow town', sport=None),
    ])
    async def test_failure_bad_request_none_data(self, bad_data, async_client, team):
        # team fixture
        # Team(id=?, name='knuckleheads', city='rain city', sport='hockey')
        team_id = team.id
        response = await async_client.put(f'/teams/{team_id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        print(res_data)
        assert res_data['detail'][0]['msg'] == 'none is not an allowed value'
        assert res_data['detail'][0]['type'] == 'type_error.none.not_allowed'

    @pytest.mark.parametrize('bad_data', [
        dict(),
        dict(name='No city or sport'),
        dict(name='OK', city='missing sport'),
        dict(name='OK', sport='no city'),
        dict(city='missing name and sport'),
        dict(city='missing name', sport='cool sport'),
        dict(sport='cool sport missing name and city'),
        dict(id=1),
        dict(id=1, city='Cow town', sport='hockey'),
        dict(id=1, name='flames', sport='hockey'),
        dict(id=1, name='flames', city='cow town'),
        dict(fake_attr='Missing name', city='Cow town', sport='hockey'),
        dict(fake_attr='Missing city', name='Flames', sport='hockey'),
        dict(fake_attr='Missing sport', name='Flames', city='Cow town'),
    ])
    async def test_failure_bad_request_missing_data(self, bad_data, async_client, team):
        # team fixture
        # Team(id=?, name='knuckleheads', city='rain city', sport='hockey')
        team_id = team.id
        response = await async_client.put(f'/teams/{team_id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        print(res_data)
        assert res_data['detail'][0]['msg'] == 'field required'
        assert res_data['detail'][0]['type'] == 'value_error.missing'

    async def test_success(self, async_client, team):
        # team fixture
        # Team(id=?, name='knuckleheads', city='rain city', sport='hockey')
        team_id = team.id
        update_data = dict(name='CanucKS', city='Rain   city', sport='hockey')
        expected_data = dict(id=team_id, name='canucks', city='rain city', sport='hockey')
        response = await async_client.put(f'/teams/{team_id}', json=update_data)
        assert response.status_code == 200
        assert response.json() == expected_data
