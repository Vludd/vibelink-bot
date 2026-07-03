from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline.onboarding import kb_onboarding_start
from app.bot.keyboards.inline.profile import kb_main_menu
from app.bot.texts import ru as texts
from app.bot.utils.messages import answer_new_message
from app.services.profile_service import ProfileService

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить Telegram-пользователя.")
        return
    
    profile_service = ProfileService(session)

    user = await profile_service.get_or_create(
        telegram_id=message.from_user.id,
        telegram_username=message.from_user.username,
    )

    user = await profile_service.sync_username(
        user=user,
        telegram_username=message.from_user.username,
    )
    
    reply_markup = kb_onboarding_start()
    if user.is_profile_complete:
        reply_markup = kb_main_menu(is_hidden=user.is_hidden)

    await answer_new_message(
        message,
        texts.start_text(message.from_user.username),
        reply_markup=reply_markup,
    )
