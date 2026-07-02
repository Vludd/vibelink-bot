from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import enum_values, get_current_user, goal_set
from app.bot.keyboards.inline.onboarding import kb_goals, kb_onboarding_start, kb_username_required
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.db.models.user import Goal
from app.services.profile_service import ProfileService

router = Router(name="onboarding_goals")


def _parse_goal_from_callback(data: str | None) -> Goal | None:
    if not data:
        return None

    value = data.removeprefix("ob:goal:")
    try:
        return Goal(value)
    except ValueError:
        return None


async def _show_goals_step(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    *,
    intro: str | None = None,
) -> None:
    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    if not user.telegram_username:
        await state.clear()
        await edit_callback_message(
            callback,
            texts.USERNAME_REQUIRED,
            reply_markup=kb_username_required(),
        )
        return

    selected_goals = goal_set(user.goals)
    await state.set_state(Onboarding.choosing_goals)
    await state.update_data(selected_goal_values=enum_values(selected_goals))

    text = texts.ASK_GOALS if intro is None else f"{intro}\n\n{texts.ASK_GOALS}"
    await edit_callback_message(callback, text, reply_markup=kb_goals(selected_goals))


@router.callback_query(F.data == "ob:how")
async def show_how_it_works(callback: CallbackQuery) -> None:
    await edit_callback_message(
        callback,
        texts.HOW_IT_WORKS,
        reply_markup=kb_onboarding_start(),
    )


@router.callback_query(F.data == "ob:start")
@router.callback_query(F.data == "ob:username:check")
async def start_onboarding(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    await _show_goals_step(callback, state, session, intro=texts.ONBOARDING_START)


@router.callback_query(Onboarding.choosing_goals, F.data.startswith("ob:goal:"))
async def toggle_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = _parse_goal_from_callback(callback.data)
    if goal is None:
        await callback.answer("Неизвестная цель.", show_alert=True)
        return

    data = await state.get_data()
    selected = goal_set(data.get("selected_goal_values"))

    if goal in selected:
        selected.remove(goal)
    else:
        selected.add(goal)

    await state.update_data(selected_goal_values=enum_values(selected))
    await edit_callback_message(callback, texts.ASK_GOALS, reply_markup=kb_goals(selected))


@router.callback_query(Onboarding.choosing_goals, F.data == "ob:done:goals")
async def save_goals(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()
    selected = goal_set(data.get("selected_goal_values"))

    if not selected:
        await callback.answer(texts.NEED_SELECT_GOAL, show_alert=True)
        return

    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    profile_service = ProfileService(session)
    await profile_service.set_goals(user, list(selected))

    await state.set_state(Onboarding.entering_name)
    await edit_callback_message(callback, texts.ASK_NAME)
