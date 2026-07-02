from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import (
    enum_values,
    get_current_user,
    goal_set,
    profile_to_payload,
)
from app.bot.keyboards.inline.onboarding import kb_goals, kb_preview_confirm
from app.bot.keyboards.inline.profile import kb_main_menu
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.services.profile_service import ProfileService

router = Router(name="onboarding_preview")


async def show_profile_preview(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    user = await get_current_user(callback, session, with_interests=True)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    await state.set_state(Onboarding.preview)
    await edit_callback_message(
        callback,
        texts.profile_preview(profile_to_payload(user)),
        reply_markup=kb_preview_confirm(),
    )


@router.callback_query(Onboarding.preview, F.data == "ob:confirm")
async def confirm_profile(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    await ProfileService(session).complete_profile(user)
    await state.clear()

    await edit_callback_message(
        callback,
        texts.PROFILE_SAVED,
        reply_markup=kb_main_menu(is_hidden=user.is_hidden),
    )


@router.callback_query(Onboarding.preview, F.data == "ob:edit")
async def restart_onboarding(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    selected_goals = goal_set(user.goals)
    await state.set_state(Onboarding.choosing_goals)
    await state.update_data(selected_goal_values=enum_values(selected_goals))

    await edit_callback_message(
        callback,
        f"{texts.ONBOARDING_RESTART}\n\n{texts.ASK_GOALS}",
        reply_markup=kb_goals(selected_goals),
    )
