from pydantic import BaseModel


class TeamBM(BaseModel):
    name: str
    city: str
    sport: str


def test_assert_team_dict():
    team_data = {'name': 'flames', 'city': 'cowtown', 'sport': 'hockey'}
    team = TeamBM(**team_data)
    assert team_data == team, 'Using BaseModel, a dict of team data == TeamBM when the'
