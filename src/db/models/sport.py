from typing import List

from pydantic import validator

from sqlalchemy import Column, Enum, String, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from src.db.models import normalize_str
from src.db.schema.league import LeagueEnum


class SportBase(SQLModel):
    name: str = Field(sa_column=Column('name', String, nullable=False, index=True))
    league: LeagueEnum = Field(sa_column=Column(Enum(LeagueEnum), nullable=False, index=True, unique=True))


class Sport(SportBase, table=True):
    __table_args__ = (
        UniqueConstraint('name', 'league', name='sport_name_league_unique_idx'),
    )

    id: int = Field(default=None, primary_key=True, nullable=False)
    teams: List["Team"] = Relationship(back_populates='sport')


class SportCreate(SportBase):
    _normalize_name = validator('name', allow_reuse=True)(normalize_str)


class SportRead(SportBase):
    id: int
