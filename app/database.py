from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


def _database_url_for_asyncpg(url: str) -> str:
    """PgBouncer transaction mode (:6543) breaks asyncpg prepared statements; prefer session port."""
    if "+asyncpg" in url and ":6543" in url:
        return url.replace(":6543", ":5432", 1)
    return url


engine = create_async_engine(
    _database_url_for_asyncpg(settings.DATABASE_URL),
    echo=False,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
