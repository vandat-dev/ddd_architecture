import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.core.setting import settings

# Global variables
async_engine = None
AsyncSessionLocal = None

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    global async_engine, AsyncSessionLocal

    try:
        # Create async engine
        async_engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("✅ Database connected successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        logger.warning("⚠️  Continuing startup without active DB connection...")
        async_engine = None
        AsyncSessionLocal = None

    yield

    if async_engine:
        await async_engine.dispose()


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
