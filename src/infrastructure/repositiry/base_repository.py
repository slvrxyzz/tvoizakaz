import asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


engine_kwargs = {
    "echo": settings.debug,
    "pool_pre_ping": settings.database_pool_pre_ping,
    "pool_recycle": settings.database_pool_recycle,
}

if settings.database_url.startswith("sqlite"):
    from sqlalchemy.pool import StaticPool

    engine_kwargs.update(
        {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        }
    )
else:
    engine_kwargs.update(
        {
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
        }
    )


engine = create_async_engine(settings.database_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

_schema_lock = asyncio.Lock()

async def ensure_database_schema() -> None:
    async with _schema_lock:
        async with engine.begin() as conn:
            def _check_and_create(sync_conn):
                inspector = inspect(sync_conn)
                missing = [
                    table.name
                    for table in Base.metadata.sorted_tables
                    if not inspector.has_table(table.name)
                ]
                if missing:
                    Base.metadata.create_all(sync_conn)
            await conn.run_sync(_check_and_create)

async def get_db():
    """Dependency для получения сессии БД"""
    await ensure_database_schema()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
