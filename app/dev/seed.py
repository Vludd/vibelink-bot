import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed_default_interests
from app.dev.db import run_in_session

logger = logging.getLogger(__name__)


async def seed_database() -> None:
    """Populate lookup tables with default data."""

    async def operation(session: AsyncSession) -> None:
        logger.info("Seeding interests...")

        await seed_default_interests(session)
        await session.commit()

    await run_in_session(operation)