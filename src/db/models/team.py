from typing import Optional

from pydantic import validator

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import SQLModel, Field, Index, Relationship

from src.db.models import normalize_str

from src.db.models.sport import Sport


class TeamBase(SQLModel):
    name: str = Field(sa_column=Column('name', String, nullable=False, index=True, unique=False))
    city: str
    sport_id: Optional[int] = Field(foreign_key='sport.id')


class TeamCreate(TeamBase):
    _normalize_name = validator('name', allow_reuse=True)(normalize_str)
    _normalize_city = validator('city', allow_reuse=True)(normalize_str)


class Team(TeamBase, table=True):
    __table_args__ = (
        UniqueConstraint('name', 'city', 'sport_id', name='team_name_city_sport_unique_idx'),
    )

    id: int = Field(default=None, primary_key=True, nullable=False)
    sport: Optional[Sport] = Relationship(back_populates='teams')


class TeamRead(TeamBase):
    id: int


class TeamReadWithSport(TeamRead):
    sport: Sport
