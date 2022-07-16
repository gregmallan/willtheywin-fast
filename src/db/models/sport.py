from typing import List

from pydantic import validator

from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field, Relationship

from src.db.models import normalize_str


class SportBase(SQLModel):
    name: str = Field(sa_column=Column('name', String, nullable=False, index=True, unique=True))


class Sport(SportBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    teams: List["Team"] = Relationship(back_populates='sport')


class SportCreate(SportBase):
    _normalize_name = validator('name', allow_reuse=True)(normalize_str)


class SportRead(SportBase):
    id: int
