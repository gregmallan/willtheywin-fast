from typing import List

from src.db.models.sport import SportRead
from src.db.models.team import TeamRead


class SportReadWithTeams(SportRead):
    teams: List[TeamRead] = []
