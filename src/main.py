from typing import List, Optional

from fastapi import Depends, FastAPI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session, init_db
from db.models import Team, TeamBase, TeamCreate
from db.schema.answer import Answer, AnswerChoices, Sentiment

app = FastAPI()


@app.get('/ping')
async def ping():
    return {'ping': 'pong!'}


@app.get('/teams', response_model=List[Team])
async def get_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    # return [Team(id=t.id, name=t.name, city=t.city, sport=t.sport) for t in teams]
    return teams


@app.post('/teams')
async def create_team(team: TeamCreate, session: AsyncSession = Depends(get_session)):
    team = Team(name=team.name, city=team.city, sport=team.sport)
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


@app.get('/teams/{team_id}')
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # Alternate option to make the query for team by id
    # query = select(Team).where(Team.id == team_id)
    # results = await session.execute(query)
    # team = results.first() # Returns a sqlalchemy Row
    # team = results.one()  # Returns a sqlalchemy Row or raises

    team = await session.get(Team, team_id)  # Returns Team instance

    if team is None:
        return {'OK': False, 'team': None, 'error': f'No matching team with id={team_id}'}

    return team


@app.put('/teams/{team_id}')
async def update_team(team_id: int, team: TeamBase, session: AsyncSession = Depends(get_session)):
    db_team = await session.get(Team, team_id)

    for field, val in team.dict().items():
        setattr(db_team, field, val)

    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)

    return db_team


@app.delete('/teams/{team_id}')
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)

    if team is None:
        return {'OK': False, 'team_id': team_id, 'error': f'No matching team with id={team_id}'}

    await session.delete(team)
    await session.commit()

    return {'OK': True, 'team': team, 'msg': f'team id={team_id} deleted'}


@app.get('/teams/{team_id}/ask')
async def team_will_they_win(team_id: int, sentiment: Optional[Sentiment] = None,
                             session: AsyncSession = Depends(get_session)):
    query = select(Team).where(Team.id == team_id)
    results = await session.execute(query)
    team = results.first()

    if team is None:
        return {'OK': False, 'team': None, 'error': f'No matching team for id={team_id}'}

    answer_choices_callable = AnswerChoices.any
    if sentiment == Sentiment.NEGATIVE:
        answer_choices_callable = AnswerChoices.negative
    elif sentiment == Sentiment.NEUTRAL:
        answer_choices_callable = AnswerChoices.neutral
    elif sentiment == Sentiment.POSITIVE:
        answer_choices_callable = AnswerChoices.positive

    answer = answer_choices_callable()
    return {'team': team, 'answer': answer, 'requested_sentiment': sentiment}
