from typing import Dict, List

import pytest

from src.db.models.sport import Sport


def sort_model_objs_by_id(models: List[Sport]):
    models.sort(key=lambda t: t.id)


def sort_model_dicts_by_id(models: List[Dict]):
    models.sort(key=lambda t: t['id'])


def not_found_response_json(sport_id):
    return {'detail': f'No sport found with id={sport_id}'}


@pytest.mark.asyncio
class TestCreateSport():

    @pytest.mark.parametrize('bad_data', [
        dict(name=None),
    ])
    async def test_failure_bad_request_none_data(self, bad_data, async_client, db):
        response = await async_client.post(f'/sports', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        assert res_data['detail'][0]['msg'] == 'none is not an allowed value'
        assert res_data['detail'][0]['type'] == 'type_error.none.not_allowed'

    @pytest.mark.parametrize('bad_data', [
        dict(),
        dict(id=1),
        dict(fake_attr='Missing name'),
    ])
    async def test_failure_bad_request_missing_data(self, bad_data, async_client, db):
        response = await async_client.post(f'/sports', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        assert res_data['detail'][0]['msg'] == 'field required'
        assert res_data['detail'][0]['type'] == 'value_error.missing'

    @pytest.mark.parametrize('sport_dict', [
        dict(name='Hockey (NHL)'),
        dict(name='hockey (NHL)'),
        dict(name='HOCKEY (NHL)'),
        dict(name='hocKeY (NHL)'),
        dict(name='hockey (NHL)'),
        dict(name='baseball (MLB)'),
        dict(name='BaSEbaLL (MLB)'),
        dict(name='BASEbALL (MLB)'),
    ])
    async def test_create_sport_already_exists(self, sport_dict, async_client, hockey, baseball):
        response = await async_client.post('/sports', json=sport_dict)
        assert response.status_code == 400
        res_data = response.json()
        assert 'IntegrityError' in res_data['detail']
        for k, v in sport_dict.items():
            assert k in res_data['detail']
            assert ' '.join(word.strip() for word in v.split(' ') if word).lower() in res_data['detail']

    @pytest.mark.parametrize('name_in, name_out', [
        ('Football (CFL)', 'football (cfl)'),
        ('Hockey  (NHL)  ', 'hockey (nhl)'),
        (' basebaLL (MBL)   ', 'baseball (mbl)'),
    ])
    async def test_create_none_exist(self, async_client, db, name_in, name_out):
        expected_sport_dict = dict(name=name_out)
        response = await async_client.post('/sports', json=dict(name=name_in))
        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == expected_sport_dict

    async def test_create_with_existing_sports(self, async_client, sports):
        sport_dict = dict(name='Curling')
        response = await async_client.post('/sports', json=sport_dict)
        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == {k: v.lower() for k, v in sport_dict.items()}

    @pytest.mark.parametrize('sport_dict', [
        dict(name='Football (CFL)'),
        dict(name='Hockey (AHL)'),
        dict(name='basketball (WNBA)'),
    ])
    async def test_create_with_similar_sports(self, sport_dict, async_client, sports):
        response = await async_client.post('/sports', json=sport_dict)

        assert response.status_code == 201
        res_data = response.json()
        assert res_data.pop('id')
        assert res_data == {k: v.lower() for k, v in sport_dict.items()}


@pytest.mark.asyncio
class TestGetSport():

    async def test_no_sports(self, async_client, db):
        non_existent_id = 1
        response = await async_client.get(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_sport_exist_invalid_id(self, async_client, hockey):
        invalid_id = hockey.name
        response = await async_client.get(f'/sports/{invalid_id}')
        assert response.status_code == 422
        res_data = response.json()
        assert 'sport_id' in res_data['detail'][0]['loc']

    async def test_single_sport_exist_not_found(self, async_client, hockey):
        non_existent_id = hockey.id + 1
        response = await async_client.get(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_single_sport_exist_found_no_teams(self, async_client, hockey):
        response = await async_client.get(f'/sports/{hockey.id}')
        assert response.status_code == 200
        hockey = hockey.dict()
        hockey['teams'] = []
        assert response.json() == hockey

    async def test_single_sport_exist_found(self, async_client, hockey_with_teams):
        hockey = hockey_with_teams[0]
        teams = hockey_with_teams[1]
        response = await async_client.get(f'/sports/{hockey.id}')
        assert response.status_code == 200

        hockey = hockey.dict()
        hockey['teams'] = [team.dict() for team in teams]

        sort_model_dicts_by_id(hockey['teams'])
        hockey_response_data = response.json()
        sort_model_dicts_by_id(hockey_response_data['teams'])

        assert hockey_response_data == hockey

    async def test_multiple_sports_exist_not_found(self, async_client, sports):
        sort_model_objs_by_id(sports)
        non_existent_id = sports[-1].id + 1
        response = await async_client.get(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_multiple_sports_exist_found(self, async_client, sports_with_teams):
        sports = sports_with_teams[0]
        sports_teams = sports_with_teams[1]
        for sport in sports:
            sport_teams = [team.dict() for team in sports_teams[sport.id]]
            sort_model_dicts_by_id(sport_teams)
            sport = sport.dict()
            sport['teams'] = sport_teams

            response = await async_client.get(f"/sports/{sport['id']}")
            sport_response_data = response.json()
            sort_model_dicts_by_id(sport_response_data['teams'])

            assert response.status_code == 200
            assert sport_response_data == sport


@pytest.mark.asyncio
class TestGetSports:

    async def test_get_sports_none_exist(self, async_client, db):
        response = await async_client.get('/sports')
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_sports(self, async_client, sports):
        response = await async_client.get('/sports')
        assert response.status_code == 200
        response_sports = response.json()
        assert response_sports
        assert len(response_sports) == len(sports)

        sort_model_dicts_by_id(response_sports)
        sort_model_objs_by_id(sports)

        # TODO: Why does pytest say list of dicts == list of Sport objects. Not using only this assertion until I know why.
        #  I think it may come from SQLModel <- pydantic BaseModel <- ModelMetaclass.
        assert response.json() == sports

        for sport_dict, sport in zip(response_sports, sports):
            assert sport_dict == sport
            assert sport_dict == sport.dict()


@pytest.mark.asyncio
class TestUpdateSport():

    async def test_no_sports(self, async_client, db):
        non_existent_id = 1
        update_data = dict(name='hockey')
        response = await async_client.put(f'/sports/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_sports_not_found(self, async_client, hockey):
        non_existent_id = hockey.id + 1
        update_data = dict(name='baseball')
        response = await async_client.put(f'/sports/{non_existent_id}', json=update_data)
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    @pytest.mark.parametrize('bad_data', [
        dict(name=None),
    ])
    async def test_failure_bad_request_none_data(self, bad_data, async_client, hockey):
        sport_id = hockey.id
        response = await async_client.put(f'/sports/{sport_id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        assert res_data['detail'][0]['msg'] == 'none is not an allowed value'
        assert res_data['detail'][0]['type'] == 'type_error.none.not_allowed'

    @pytest.mark.parametrize('bad_data', [
        dict(),
        dict(id=1),
        dict(fake_attr='Missing name'),
    ])
    async def test_failure_bad_request_missing_data(self, bad_data, async_client, hockey):
        sport_id = hockey.id
        response = await async_client.put(f'/sports/{sport_id}', json=bad_data)
        res_data = response.json()
        assert response.status_code == 422
        assert res_data['detail'][0]['msg'] == 'field required'
        assert res_data['detail'][0]['type'] == 'value_error.missing'

    async def test_success(self, async_client, hockey):
        sport_id = hockey.id
        update_data = dict(name='hockey   (AHL)')
        expected_data = dict(id=sport_id, name='hockey (ahl)')
        response = await async_client.put(f'/sports/{sport_id}', json=update_data)
        assert response.status_code == 200
        assert response.json() == expected_data


@pytest.mark.asyncio
class TestDeleteSport():

    async def test_no_sports(self, async_client, db):
        non_existent_id = 1
        response = await async_client.delete(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_sport_exist_invalid_id(self, async_client, hockey):
        invalid_id = hockey.name
        response = await async_client.delete(f'/sports/{invalid_id}')
        assert response.status_code == 422
        res_data = response.json()
        assert 'sport_id' in res_data['detail'][0]['loc']

    async def test_single_sport_exist_not_found(self, async_client, hockey):
        non_existent_id = hockey.id + 1
        response = await async_client.delete(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_single_sport_exist_found(self, async_client, hockey):
        response = await async_client.delete(f'/sports/{hockey.id}')
        assert response.status_code == 200
        assert response.json() == {'OK': True, 'sport': hockey, 'msg': f'sport id={hockey.id} deleted'}

    async def test_multiple_sports_exist_not_found(self, async_client, sports):
        sort_model_objs_by_id(sports)
        non_existent_id = sports[-1].id + 1
        response = await async_client.delete(f'/sports/{non_existent_id}')
        assert response.status_code == 404
        assert response.json() == not_found_response_json(non_existent_id)

    async def test_multiple_sports(self, async_client, sports):
        sport = sports[0]
        response = await async_client.delete(f'/sports/{sport.id}')
        assert response.status_code == 200
        assert response.json() == {'OK': True, 'sport': sport, 'msg': f'sport id={sport.id} deleted'}