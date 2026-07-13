from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.bot.dependencies import (
    build_engine,
    build_session_factory,
)

from app.bot.dependencies import build_engine
from app.db.base import Base

import logging

logger = logging.getLogger(__name__)


async def _run(
    operation: Callable[[AsyncConnection], Awaitable[None]],
) -> None:
    """Run a database operation using a temporary engine."""

    engine = build_engine()

    try:
        async with engine.begin() as conn:
            await operation(conn)
    finally:
        await engine.dispose()
        
async def create_database() -> None:
    """Create all database tables."""

    async def operation(conn: AsyncConnection) -> None:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Creating database...")
    await _run(operation)
    
async def drop_database() -> None:
    """Drop all database tables."""

    async def operation(conn: AsyncConnection) -> None:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Dropping database...")
    await _run(operation)
    
async def reset_database() -> None:
    """Drop and recreate all database tables."""

    async def operation(conn: AsyncConnection) -> None:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Resetting database...")
    await _run(operation)
    
async def wipe_database() -> None:
    """
    Remove all user-generated data while keeping lookup tables.
    """

    async def operation(conn: AsyncConnection) -> None:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    logger.info("Wiping database...")
    await _run(operation)
    
async def run_in_connection(
    operation: Callable[[AsyncConnection], Awaitable[None]],
) -> None:
    """Run a database operation using a temporary engine."""

    engine = build_engine()

    try:
        async with engine.begin() as conn:
            await operation(conn)
    finally:
        await engine.dispose()


async def run_in_session(
    operation: Callable[[AsyncSession], Awaitable[None]],
) -> None:
    """Run a session operation using a temporary engine."""

    engine = build_engine()
    session_factory = build_session_factory(engine)

    try:
        async with session_factory() as session:
            await operation(session)
    finally:
        await engine.dispose()
        
        