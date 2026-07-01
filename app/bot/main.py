from __future__ import annotations

import asyncio
import importlib
import logging
import os
from collections.abc import Iterable
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, Message

from app.bot.config import settings
from app.bot.keyboards.inline.match import kb_match_actions
from app.bot.keyboards.inline.profile import kb_main_menu
from app.bot.keyboards.inline.search import kb_candidate_card
from app.bot.logger import setup_logger

from app.bot.texts import ru as texts

logger = logging.getLogger(__name__)

HANDLER_MODULES: tuple[str, ...] = (
    "app.bot.handlers.start",
    "app.bot.handlers.onboarding.goals",
    "app.bot.handlers.onboarding.profile",
    "app.bot.handlers.onboarding.interests",
    "app.bot.handlers.onboarding.description",
    "app.bot.handlers.onboarding.photo",
    "app.bot.handlers.onboarding.privacy",
    "app.bot.handlers.onboarding.preview",
    "app.bot.handlers.search",
    "app.bot.handlers.matching",
    "app.bot.handlers.profile_menu",
    "app.bot.handlers.settings",
    "app.bot.handlers.moderation",
)


def _log_level() -> int:
    return getattr(logging, settings.log_level.upper(), logging.INFO)


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    storage_mode = os.getenv("FSM_STORAGE", "memory").lower().strip()

    if storage_mode == "redis":
        storage = RedisStorage.from_url(settings.redis_url)
        logger.info("FSM storage: RedisStorage(%s)", settings.redis_url)
    else:
        storage = MemoryStorage()
        logger.info("FSM storage: MemoryStorage")

    return Dispatcher(storage=storage)


def _get_router(module: Any) -> Router | None:
    router = getattr(module, "router", None)
    if isinstance(router, Router):
        return router
    return None


def include_project_routers(dp: Dispatcher, modules: Iterable[str] = HANDLER_MODULES) -> None:
    for module_path in modules:
        module = importlib.import_module(module_path)
        router = _get_router(module)

        if router is None:
            logger.debug("Router skipped: %s has no `router`", module_path)
            continue

        dp.include_router(router)
        logger.info("Router included: %s", module_path)


def build_dev_router() -> Router:
    """
    Temporary smoke-test router.

    Remove this router after normal handlers are implemented.

    It lets you test that:
    - bot starts;
    - commands work;
    - inline keyboards render;
    - mock templates look readable in Telegram.
    """

    router = Router(name="dev")

    @router.message(Command("ping"))
    async def cmd_ping(message: Message) -> None:
        await message.answer("pong ✅")

    @router.message(Command("mock_profile"))
    async def cmd_mock_profile(message: Message) -> None:
        await message.answer(
            texts.profile_preview(texts.MOCK_PROFILE),
            reply_markup=kb_main_menu(),
        )

    @router.message(Command("mock_candidate"))
    async def cmd_mock_candidate(message: Message) -> None:
        await message.answer(
            texts.candidate_card(texts.MOCK_CANDIDATE),
            reply_markup=kb_candidate_card(candidate_id=texts.MOCK_CANDIDATE["id"]),
        )

    @router.message(Command("mock_match"))
    async def cmd_mock_match(message: Message) -> None:
        await message.answer(
            texts.match_created(
                matched_user=texts.MOCK_CANDIDATE,
                common_interests=texts.MOCK_CANDIDATE["common_interests"],
            ),
            reply_markup=kb_match_actions(
                matched_user_id=texts.MOCK_CANDIDATE["id"],
                telegram_username=texts.MOCK_CANDIDATE["telegram_username"],
            ),
        )

    @router.callback_query(F.data == "menu:back")
    @router.callback_query(F.data.startswith("menu:"))
    @router.callback_query(F.data.startswith("card:"))
    @router.callback_query(F.data.startswith("match:"))
    
    async def dev_callback_stub(callback: CallbackQuery) -> None:
        await callback.answer("Пока это dev-заглушка ✅", show_alert=False)

    return router


async def main() -> None:
    setup_logger(_log_level())

    bot = create_bot()
    dp = create_dispatcher()

    include_project_routers(dp)

    dp.include_router(build_dev_router())

    logger.info("Starting VibeLink bot polling")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        await dp.storage.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()