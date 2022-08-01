import asyncio
from typing import List

from src.db.data import teams
from src.db.models.team import Team, TeamCreate
from src.db.models.sport import Sport, SportCreate
from src.db.schema.league import LeagueEnum
from src.db.db import get_session_with_engine, engine


async def seed_sports() -> dict:
    print('Seeding sports...')

    sports_create = [
        SportCreate(name='Hockey', league=LeagueEnum.NHL),
        SportCreate(name='Baseball', league=LeagueEnum.MLB),
        SportCreate(name='Football', league=LeagueEnum.NFL),
        SportCreate(name='Football', league=LeagueEnum.CFL),
    ]

    db_session = get_session_with_engine(engine)

    sports = []

    try:
        for i, sport in enumerate(sports_create):
            sport = Sport(**sport.dict())
            print(sport)
            db_session.add(sport)
            sports.append(sport)

        await db_session.commit()

        sports_dict = {}
        for s in sports:
            await db_session.refresh(s)
            sports_dict[s.league] = s

    finally:
        if db_session:
            await db_session.close()

    print('Done seeding sports')
    print(sports)

    return sports_dict


async def seed_all_leagues() -> None:
    sports_dict = await seed_sports()

    await seed_teams_for_sport(sports_dict[LeagueEnum.NHL], teams.NHL)
    await seed_teams_for_sport(sports_dict[LeagueEnum.MLB], teams.MLB)
    await seed_teams_for_sport(sports_dict[LeagueEnum.NFL], teams.NFL)
    await seed_teams_for_sport(sports_dict[LeagueEnum.CFL], teams.CFL)


async def seed_teams_for_sport(sport: Sport, teams: List[tuple]) -> List[Team]:
    print(f'Seeding teams for sport {sport}...')

    team_creates = [TeamCreate(city=tt[0], name=tt[1]) for tt in teams]

    db_session = get_session_with_engine(engine)

    db_teams = []
    try:

        for tc in team_creates:
            team = Team(**tc.dict(), sport=sport)
            db_session.add(team)
            db_teams.append(team)

        await db_session.commit()

        for t in db_teams:
            await db_session.refresh(t)

    finally:
        if db_session:
            await db_session.close()

    print(f'Done seeding teams for sport {sport}')

    return db_teams


async def main() -> asyncio.coroutine:
    await seed_all_leagues()


if __name__ == '__main__':
    asyncio.run(main())
