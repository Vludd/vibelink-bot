from collections.abc import AsyncIterator
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.bot.config import settings


def build_engine() -> AsyncEngine:
    return create_async_engine(settings.database_url, echo=settings.db_echo, pool_pre_ping=True)


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


def build_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def build_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher(redis: Redis) -> Dispatcher:
    storage = RedisStorage(redis=redis)
    return Dispatcher(storage=storage)


@dataclass
class AppContainer:
    """Bundles every shared resource the app needs. Built once in main.py,
    then injected into aiogram handlers via workflow_data / middlewares,
    and reused directly by services and repositories.
    """

    bot: Bot
    dispatcher: Dispatcher
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis

    async def aclose(self) -> None:
        await self.engine.dispose()
        await self.redis.aclose()
        await self.bot.session.close()


def build_container() -> AppContainer:
    engine = build_engine()
    session_factory = build_session_factory(engine)
    redis = build_redis()
    bot = build_bot()
    dispatcher = build_dispatcher(redis)

    return AppContainer(
        bot=bot,
        dispatcher=dispatcher,
        engine=engine,
        session_factory=session_factory,
        redis=redis,
    )


async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Yields a session that commits on success and rolls back on error.
    Used by db_session middleware to provide a fresh session per update,
    and reusable directly in scripts/tests.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise