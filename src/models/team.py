from pydantic import BaseModel


class Team(BaseModel):
    name: str
    city: str
    sport: str
