from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.db.models.team import Team, TeamCreate, TeamReadWithSport
from src.db.models.sport import Sport, SportCreate
from src.db.models.related import SportReadWithTeams
from src.db.schema.answer import AnswerChoices, Sentiment
from src.response_exception import HTTPBadRequest, HTTPExceptionNotFound

DISABLE_CUD_ROUTES = True

SENTIMENT_CHOICES_CALLABLE_MAP = {
    Sentiment.NEGATIVE: AnswerChoices.negative,
    Sentiment.NEUTRAL: AnswerChoices.neutral,
    Sentiment.POSITIVE: AnswerChoices.positive,
}

origins = [
    "https://gregmallan.github.io/",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='https?://127.0.0.1:\d*',
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", ],
    allow_headers=["*"],
)


def protect_route():
    if DISABLE_CUD_ROUTES:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.get('/ping', response_model=Dict)
async def ping():
    return {'ping': 'pong!'}


@app.get('/sports', response_model=List[SportReadWithTeams])
async def get_sports(session: AsyncSession = Depends(get_session)):
    results = await session.execute(
        select(Sport).options(selectinload(Sport.teams)).execution_options(populate_existing=True)
    )

    sports = results.scalars().all()
    return sports


@app.post('/sports', response_model=Sport, status_code=status.HTTP_201_CREATED, dependencies=[Depends(protect_route)])
async def create_sport(sport: SportCreate, session: AsyncSession = Depends(get_session)):
    sport = Sport.from_orm(sport)
    session.add(sport)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPBadRequest(f'IntegrityError creating Sport: {sport.dict()}')

    await session.refresh(sport)
    return sport


@app.get('/sports/{sport_id}', response_model=SportReadWithTeams)
async def get_sport(sport_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Sport, Team)
            .join(Team, Team.sport_id == Sport.id, isouter=True)  # Do a left outer join to get sports with no teams
            .where(Sport.id == sport_id)
            .options(selectinload(Sport.teams))
    )

    sport = result.scalar()

    if sport is None:
        raise HTTPExceptionNotFound(f'No sport found with id={sport_id}')

    return sport


@app.put('/sports/{sport_id}', response_model=Sport, status_code=status.HTTP_200_OK,
         dependencies=[Depends(protect_route)])
async def update_sport(sport_id: int, sport: SportCreate, session: AsyncSession = Depends(get_session)):
    db_sport = await session.get(Sport, sport_id)

    if db_sport is None:
        raise HTTPExceptionNotFound(f'No sport found with id={sport_id}')

    for field, val in sport.dict().items():
        setattr(db_sport, field, val)

    session.add(db_sport)
    await session.commit()
    await session.refresh(db_sport)

    return db_sport


@app.delete('/sports/{sport_id}', response_model=Dict, status_code=status.HTTP_200_OK,
            dependencies=[Depends(protect_route)])
async def delete_sport(sport_id: int, session: AsyncSession = Depends(get_session)):
    sport = await session.get(Sport, sport_id)

    if sport is None:
        raise HTTPExceptionNotFound(f'No sport found with id={sport_id}')

    await session.delete(sport)
    await session.commit()

    return {'OK': True, 'sport': sport, 'msg': f'sport id={sport_id} deleted'}


@app.get('/teams', response_model=List[TeamReadWithSport])
async def get_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team, Sport).join(Sport).options(selectinload(Team.sport)))
    teams = result.scalars().all()
    return teams


@app.post('/teams', response_model=Team, status_code=status.HTTP_201_CREATED, dependencies=[Depends(protect_route)])
async def create_team(team: TeamCreate, session: AsyncSession = Depends(get_session)):
    team = Team(name=team.name, city=team.city, sport_id=team.sport_id)
    session.add(team)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPBadRequest(f'IntegrityError creating Team: {team.dict()}')

    await session.refresh(team)
    return team


@app.get('/teams/{team_id}', response_model=TeamReadWithSport)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    # Alternate option to make the query for team by id
    # query = select(Team).where(Team.id == team_id)
    # results = await session.execute(query)
    # team = results.first() # Returns a sqlalchemy Row
    # team = results.one()  # Returns a sqlalchemy Row or raises
    # team = await session.get(Team, team_id)  # Returns Team instance

    result = await session.execute(
        select(Team, Sport)
            .join(Sport)
            .where(Team.id == team_id)
            .options(selectinload(Team.sport))
    )

    team = result.scalar()

    if team is None:
        raise HTTPExceptionNotFound(f'No team found with id={team_id}')

    return team


@app.get('/teams/name/{team_name}', response_model=List[Team])
async def get_team_by_name(team_name: str, session: AsyncSession = Depends(get_session)):
    query = select(Team).where(Team.name == team_name.strip().lower())
    result = await session.execute(query)
    teams = result.scalars().all()

    if not teams:
        raise HTTPExceptionNotFound(f'No teams found with name={team_name}')

    return teams


@app.put('/teams/{team_id}', response_model=Team, status_code=status.HTTP_200_OK, dependencies=[Depends(protect_route)])
async def update_team(team_id: int, team: TeamCreate, session: AsyncSession = Depends(get_session)):
    db_team = await session.get(Team, team_id)

    if db_team is None:
        raise HTTPExceptionNotFound(f'No team found with id={team_id}')

    for field, val in team.dict().items():
        setattr(db_team, field, val)

    session.add(db_team)

    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPBadRequest(f'IntegrityError updating Team: {team.dict()}')

    await session.refresh(db_team)

    return db_team


@app.delete(
    '/teams/{team_id}', response_model=Dict, status_code=status.HTTP_200_OK, dependencies=[Depends(protect_route)]
)
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)

    if team is None:
        raise HTTPExceptionNotFound(f'No team found with id={team_id}')

    await session.delete(team)
    await session.commit()

    return {'OK': True, 'team': team, 'msg': f'team id={team_id} deleted'}


@app.get('/teams/{team_id}/ask', response_model=Dict)
async def team_will_they_win(team_id: int, sentiment: Optional[Sentiment] = None,
                             session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)

    if team is None:
        raise HTTPExceptionNotFound(f'No team found with id={team_id}')

    answer = SENTIMENT_CHOICES_CALLABLE_MAP.get(sentiment, AnswerChoices.any)()

    return {'team': team, 'answer': answer, 'requested_sentiment': sentiment}
