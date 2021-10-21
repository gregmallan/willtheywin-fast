from enum import Enum
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


# TODO: Refactor out models and classes
class Team(BaseModel):
    name: str
    sport: str


app = FastAPI()


@app.get('/')
async def read_root():
    return {'msg': 'Will they win???'}


@app.get('/ask/{team}')
async def will_they_win(team: str, sentiment: Optional[str] = None):
    return {'team': team, 'answer': 'Nope', 'sentiment': sentiment}


@app.post('/team/create')
async def create_team(team: Team):
    return {'team': team, 'status': 'OK'}
