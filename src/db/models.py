from typing import Optional

from sqlmodel import SQLModel, Field


class TeamBase(SQLModel):
    name: str
    city: str
    sport: str


class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)
    # name = Column(String, index=True)  # TODO: How to add index


class TeamCreate(TeamBase):
    pass
