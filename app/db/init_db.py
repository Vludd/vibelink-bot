from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text

from app.bot.dependencies import build_engine
from app.db.base import Base

# Important: import all models so Base.metadata sees every table.
import app.db.models  # noqa: F401


logger = logging.getLogger(__name__)


async def init_db() -> None:
    engine = build_engine()

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully")
    finally:
        await engine.dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())


if __name__ == "__main__":
    main()