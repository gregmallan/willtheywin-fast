import os

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = os.environ.get('DATABASE_URL')
ECHO_DB_QUERIES = bool(os.environ.get('ECHO_DB_QUERIES', 0))


def create_async_db_engine(db_url, echo=False) -> AsyncEngine:
    return create_async_engine(db_url, connect_args={'check_same_thread': False}, echo=echo, future=True)


engine = create_async_db_engine(DATABASE_URL, ECHO_DB_QUERIES)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def init_db_with_engine(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def reset_db_with_engine(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)
    async with async_session() as session:
        yield session


def get_session_with_engine(engine) -> AsyncSession:
    """Make and return an AsyncSession. Note: this session must be closed after use."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)
    return async_session()
