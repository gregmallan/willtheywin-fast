from typing import List, Optional

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session, init_db
from db.models import Team, TeamCreate
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
