from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import get_current_user
from app.bot.handlers.onboarding.preview import show_profile_preview
from app.bot.keyboards.inline.onboarding import kb_privacy
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.services.profile_service import ProfileService

router = Router(name="onboarding_privacy")

_PRIVACY_FIELDS = {"show_age", "show_city"}


def _bool_from_callback(value: str) -> bool | None:
    if value == "1":
        return True
    if value == "0":
        return False
    return None


async def _privacy_flags(state: FSMContext) -> tuple[bool, bool]:
    data = await state.get_data()
    return bool(data.get("show_age", True)), bool(data.get("show_city", True))


@router.callback_query(Onboarding.choosing_privacy, F.data.startswith("ob:priv:"))
async def toggle_privacy(callback: CallbackQuery, state: FSMContext) -> None:
    parts = (callback.data or "").split(":")

    if len(parts) != 4:
        await callback.answer("Неизвестная настройка.", show_alert=True)
        return

    _, _, field, raw_value = parts

    if field not in _PRIVACY_FIELDS:
        await callback.answer("Неизвестная настройка.", show_alert=True)
        return

    value = _bool_from_callback(raw_value)
    if value is None:
        await callback.answer("Неизвестное значение.", show_alert=True)
        return

    await state.update_data({field: value})
    show_age, show_city = await _privacy_flags(state)

    await edit_callback_message(
        callback,
        texts.ASK_PRIVACY,
        reply_markup=kb_privacy(show_age=show_age, show_city=show_city),
    )


@router.callback_query(Onboarding.choosing_privacy, F.data == "ob:done:privacy")
async def save_privacy(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    show_age, show_city = await _privacy_flags(state)
    await ProfileService(session).set_privacy(user, show_age=show_age, show_city=show_city)

    await show_profile_preview(callback, state, session)
