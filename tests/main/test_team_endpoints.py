from typing import Dict, List

import pytest

from sqlmodel import select

from src.db.models.team import Team
from src.db.models.sport import Sport, SportCreate
from src.db.schema.answer import Answer, AnswerChoices, Sentiment
from src.db.schema.league import LeagueEnum


def not_found_response_json(team_id):
    return {'detail': f'No team found with id={team_id}'}


@pytest.mark.asyncio
class TestCreateTeam():

    @pytest.mark.parametrize('bad_data,status_code', [
        (dict(name=None, city='cow town'), 422),
        (dict(name='Flames', city=None), 422),
        (dict(name='Flames', city='Cow town', sport_id=None), 400),
    ])
    async def test_failure_bad_request_none_data(self, bad_data, status_code, async_client, db, hockey):
        if 'sport_id' not in bad_data:
            bad_data['sport_id'] = hockey.id
        response = await async_client.post(f'/teams', json=bad_data)
        res_data = response.json()

        assert response.status_code == status_code
        if status_code == 400:
            assert 'IntegrityError creating Team' in res_data['detail']
        else:
            assert res_data['detail'][0]['msg'] == 'none is not an allowed value'
            assert res_data['detail'][0]['type'] == 'type_error.none.not_allowed'

    @pytest.mark.parametrize('bad_data,status_code', [
        (dict(), 422),
        (dict(name='No city or sport'), 422),
        (dict(name='OK', city='missing sport'), 400),
        (dict(name='OK', sport_id=None), 422),
        (dict(city='missing name and sport'), 422),
        (dict(city='missing name', sport_id=None), 422),
        (dict(sport_id=None), 422),
        (dict(id=1), 422),
        (dict(id=1, city='Cow town', sport_id=None), 422),
        (dict(id=1, name='flames', sport_id=None), 422),
        (dict(id=1, name='flames', city='cow town'), 400),
        (dict(fake_attr='Missing name', city='Cow town', sport_id=None), 422),
        (dict(fake_attr='Missing city', name='Flames', sport_id=None), 422),
        (dict(fake_attr='Missing sport', name='Flames', city='Cow town'), 400),
    ])
    async def test_failure_bad_request_missing_data(self, bad_data, status_code, async_client, db, hockey):
        # presence of sport_id key means to set it with fixture.  If not present we are testing that it is missing.
        if 'sport_id' in bad_data:
            bad_data['sport_id'] = hockey.id

        response = await async_client.post(f'/teams', json=bad_data)
        res_data = response.json()

        assert response.status_code == status_code
        if status_code == 400:
            assert 'IntegrityError creating Team' in res_data['detail']
        else:
            assert res_data['detail'][0]['msg'] == 'field required'
            assert res_data['detail'][0]['type'] == 'value_error.missing'

    @pytest.mark.parametrize('team_dict', [
        dict(name='Knuckleheads', city='Rain city'),
        dict(name='knuckleheads', city='rain city'),
        dict(name='KNUCKLEHEADS', city='RAIN CITY'),
        dict(name='knUCKLEHEaDS', city='RaIn cITY'),
        dict(name='knuckleheads', city='rain  city'),
    ])
    async def test_create_team_already_exists(self, team_dict, async_client, team):
        team_dict['sport_id'] = team.sport.id

        response = await async_client.post('/teams', json=team_dict)

        assert response.status_code == 400
        res_data = response.json()
        assert 'IntegrityError' in res_data['detail']
        for k, v in team_dict.items():
            assert k in res_data['detail']
            if k != 'sport_id':
                assert ' '.join(word.strip() for word in v.split(' ') if word).lower() in res_data['detail']

    async def test_create_none_exist(self, async_client, db, hockey):
        team_dict = dict(name='Knuckleheads', city='Rain  city', sport_id=hockey.id)
        expected_team_dict = dict(name='knuckleheads', city='rain city', sport_id=hockey.id)

        response = await async_client.post('/teams', json=team_dict)

        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == expected_team_dict

    async def test_create_with_existing_teams(self, async_client, teams, hockey):
        team_dict = dict(name='Canucks', city='Vancouver', sport_id=hockey.id)

        response = await async_client.post('/teams', json=team_dict)

        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data.pop('sport_id') == team_dict.pop('sport_id')
        assert res_data == {k: v.lower() for k, v in team_dict.items()}

    @pytest.mark.parametrize('team_dict,sport_name,league', [
        (dict(name='Canucks', city='Rain city'), 'hockey', LeagueEnum.NHL),
        (dict(name='Flames', city='Calgary'), 'hockey', LeagueEnum.NHL),
        (dict(name='Flames', city='CowTown'), 'hockey', LeagueEnum.NHL),
        # name='Flames', city='Cow town' in teams fixture
        (dict(name='Blue Jays', city='Toronto'), 'baseball', LeagueEnum.MLB),
        (dict(name='Raptors', city='Toronto'), 'basketball', LeagueEnum.NBA),
    ])
    async def test_create_with_similar_teams(self, team_dict, sport_name, league, async_client, teams, db_session):
        result = await db_session.execute(select(Sport).where(Sport.name == sport_name, Sport.league == league))
        sport = result.scalars().one()
        team_dict['sport_id'] = sport.id

        response = await async_client.post('/teams', json=team_dict)

        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data.pop('sport_id') == team_dict.pop('sport_id')
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
        sport = team.sport
        team = team.dict()
        team['sport'] = sport

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

            sport = team.sport
            team = team.dict()
            team['sport'] = sport

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
        assert len(response_teams) == len(teams)

        sort_team_dicts_by_id(response_teams)
        sort_team_objs_by_id(teams)

        teams_list = []
        for team in teams:
            sport = team.sport
            team = team.dict()
            team['sport'] = sport
            teams_list.append(team)

        assert response.json() == teams_list


@pytest.mark.asyncio
class TestUpdateTeam():

    async def test_no_teams(self, async_client, db):
        non_existent_id = 1
        update_data = dict(name='Canucks', city='Rain city')
        response = await async_client.put(f'/teams/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_teams_not_found(self, async_client, team):
        non_existent_id = team.id + 1
        update_data = dict(name='Canucks', city='Rain city')
        response = await async_client.put(f'/teams/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    @pytest.mark.parametrize('bad_data,status_code', [
        (dict(name=None, city='cow town'), 422),
        (dict(name='Flames', city=None), 422),
        (dict(name='Flames', city='Cow town', sport_id=None), 400),
    ])
    async def test_failure_bad_request_none_data(self, bad_data, status_code, async_client, team):

        if 'sport_id' not in bad_data:
            bad_data['sport_id'] = team.sport.id

        response = await async_client.put(f'/teams/{team.id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == status_code

        if status_code == 400:
            assert 'IntegrityError updating Team' in res_data['detail']
        else:
            assert res_data['detail'][0]['msg'] == 'none is not an allowed value'
            assert res_data['detail'][0]['type'] == 'type_error.none.not_allowed'

    @pytest.mark.parametrize('bad_data,status_code', [
        (dict(), 422),
        (dict(name='No city or sport'), 422),
        (dict(name='OK', city='missing sport'), 400),
        (dict(name='OK', sport_id=None), 422),
        (dict(city='missing name and sport'), 422),
        (dict(city='missing name', sport_id=None), 422),
        (dict(sport_id=None), 422),
        (dict(id=1), 422),
        (dict(id=1, city='Cow town', sport_id=None), 422),
        (dict(id=1, name='flames', sport_id=None), 422),
        (dict(id=1, name='flames', city='cow town'), 400),
        (dict(fake_attr='Missing name', city='Cow town', sport_id=None), 422),
        (dict(fake_attr='Missing city', name='Flames', sport_id=None), 422),
        (dict(fake_attr='Missing sport', name='Flames', city='Cow town'), 400),
    ])
    async def test_failure_bad_request_missing_data(self, bad_data, status_code, async_client, team):

        if 'sport_id' in bad_data:
            bad_data['sport_id'] = team.sport.id

        team_id = team.id

        response = await async_client.put(f'/teams/{team_id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == status_code

        if status_code == 400:
            assert 'IntegrityError updating Team' in res_data['detail']
        else:
            assert res_data['detail'][0]['msg'] == 'field required'
            assert res_data['detail'][0]['type'] == 'value_error.missing'

    async def test_success(self, async_client, team):
        team_id = team.id
        update_data = dict(name='CanucKS', city='Rain   city', sport_id=team.sport.id)
        expected_data = dict(id=team_id, name='canucks', city='rain city', sport_id=team.sport.id)
        response = await async_client.put(f'/teams/{team_id}', json=update_data)
        assert response.status_code == 200
        assert response.json() == expected_data


@pytest.mark.asyncio
class TestDeleteTeam():

    async def test_no_teams(self, async_client, db):
        non_existent_id = 1
        response = await async_client.delete(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_team_exist_invalid_id(self, async_client, team):
        invalid_id = team.name
        response = await async_client.delete(f'/teams/{invalid_id}')
        assert response.status_code == 422
        res_data = response.json()
        assert 'team_id' in res_data['detail'][0]['loc']

    async def test_single_team_exist_not_found(self, async_client, team):
        non_existent_id = team.id + 1
        response = await async_client.delete(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_single_team_exist_found(self, async_client, team):
        response = await async_client.delete(f'/teams/{team.id}')
        assert response.status_code == 200
        assert response.json() == {'OK': True, 'team': team, 'msg': f'team id={team.id} deleted'}

    async def test_multiple_teams_exist_not_found(self, async_client, teams):
        sort_team_objs_by_id(teams)
        non_existent_id = teams[-1].id + 1
        response = await async_client.delete(f'/teams/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_multiple_teams(self, async_client, teams):
        team = teams[0]
        response = await async_client.delete(f'/teams/{team.id}')
        assert response.status_code == 200
        assert response.json() == {'OK': True, 'team': team, 'msg': f'team id={team.id} deleted'}


@pytest.mark.asyncio
class TestTeamAsk():

    async def test_no_teams(self, async_client, db):
        non_existent_id = 1
        response = await async_client.get(f'/teams/{non_existent_id}/ask')
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
        response = await async_client.get(f'/teams/{non_existent_id}/ask')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_team_exist_no_sentiment(self, async_client, team):
        response = await async_client.get(f'/teams/{team.id}/ask')
        assert response.status_code == 200
        res_data = response.json()
        assert res_data['team'] == team
        assert res_data['answer']['text'] in AnswerChoices._PHRASES_ANY
        assert res_data['answer']['sentiment'] in Sentiment.POSITIVE or Sentiment.NEUTRAL or Sentiment.NEGATIVE

    @pytest.mark.parametrize('valid_sentiment', [s.value for s in Sentiment])
    @pytest.mark.parametrize('query_str_param', ['s', 'sent', 'feels', 'sentimet', ])
    async def test_team_exist_invalid_sentiment_query_param(self, query_str_param, valid_sentiment, async_client, team):
        """
        Test that an invalid query string param close to 'sentiment returns an answer from any sentiment and
        requested sentiment is null/None.
        """
        response = await async_client.get(f'/teams/{team.id}/ask', params={query_str_param: valid_sentiment})
        assert response.status_code == 200
        res_data = response.json()
        assert res_data['team'] == team
        assert res_data['requested_sentiment'] == None
        assert res_data['answer'] in AnswerChoices.ANSWERS_ANY

    @pytest.mark.parametrize('sentiment', [s.value for s in Sentiment])
    async def test_team_exist_valid_sentiment(self, sentiment, async_client, team):
        response = await async_client.get(f'/teams/{team.id}/ask', params={'sentiment': sentiment})
        assert response.status_code == 200
        res_data = response.json()
        assert res_data['team'] == team
        assert res_data['requested_sentiment'] == sentiment
        assert res_data['answer'] in getattr(AnswerChoices, f'ANSWERS_{sentiment.upper()}')
