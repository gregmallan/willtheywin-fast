from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel, Session

# Sqlite sync
# DATABASE_URL = "sqlite:///../test.db"

# Sqlite async
DATABASE_URL = "sqlite+aiosqlite:///willtheywinfastapi-dev.db"

# Postgres sync
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

# Postgres async
# DATABASE_URL = "postgresql+asyncpg://user:password@postgresserver/db"


def create_async_db_engine(db_url) -> AsyncEngine:
    return create_async_engine(db_url, connect_args={'check_same_thread': False}, echo=True, future=True)


engine = create_async_db_engine(DATABASE_URL)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
