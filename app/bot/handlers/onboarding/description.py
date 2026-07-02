from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import get_current_user
from app.bot.keyboards.inline.onboarding import kb_photo_choice
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import answer_new_message
from app.services.profile_service import ProfileService

router = Router(name="onboarding_description")

MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 500


def _clean_description(value: str | None) -> str:
    return " ".join((value or "").strip().split())[:MAX_DESCRIPTION_LENGTH]


@router.message(Onboarding.entering_description, F.text)
async def save_description(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    description = _clean_description(message.text)

    if len(description) < MIN_DESCRIPTION_LENGTH:
        await answer_new_message(message, texts.INVALID_DESCRIPTION)
        return

    user = await get_current_user(message, session)
    if user is None:
        await message.answer("Не удалось определить пользователя.")
        return

    await ProfileService(session).update(user, description=description)
    await state.set_state(Onboarding.choosing_photo)
    await answer_new_message(
        message,
        texts.ASK_PHOTO,
        reply_markup=kb_photo_choice(),
    )


@router.message(Onboarding.entering_description)
async def invalid_description(message: Message, state: FSMContext) -> None:
    await answer_new_message(message, texts.INVALID_DESCRIPTION)
