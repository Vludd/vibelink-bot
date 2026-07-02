from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import enum_or_none, get_current_user
from app.bot.keyboards.inline.onboarding import (
    kb_gender,
    kb_interest_categories,
    kb_search_scope,
)
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import answer_new_message, edit_callback_message
from app.db.models.user import Gender, SearchScope
from app.services.profile_service import ProfileService

router = Router(name="onboarding_profile")

MIN_AGE = 13
MAX_AGE = 100


def _clean_text(value: str | None, *, max_len: int) -> str:
    return " ".join((value or "").strip().split())[:max_len]


def _is_valid_name(name: str) -> bool:
    if len(name) < 2 or len(name) > 64:
        return False
    return any(ch.isalpha() for ch in name)


def _is_valid_city(city: str) -> bool:
    if len(city) < 2 or len(city) > 64:
        return False
    return any(ch.isalpha() for ch in city)


async def _ask_interests(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Onboarding.choosing_interest_categories)
    await state.update_data(selected_interest_ids=[])
    await edit_callback_message(
        callback,
        texts.ASK_INTEREST_CATEGORIES,
        reply_markup=kb_interest_categories(),
    )


async def _ask_interests_from_message(message: Message, state: FSMContext) -> None:
    await state.set_state(Onboarding.choosing_interest_categories)
    await state.update_data(selected_interest_ids=[])
    await answer_new_message(
        message,
        texts.ASK_INTEREST_CATEGORIES,
        reply_markup=kb_interest_categories(),
    )


@router.message(Onboarding.entering_name, F.text)
async def save_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    name = _clean_text(message.text, max_len=64)

    if not _is_valid_name(name):
        await answer_new_message(message, texts.INVALID_NAME)
        return

    user = await get_current_user(message, session)
    if user is None:
        await message.answer("Не удалось определить пользователя.")
        return

    await ProfileService(session).update(user, name=name)
    await state.set_state(Onboarding.entering_age)
    await answer_new_message(message, texts.ASK_AGE)


@router.message(Onboarding.entering_name)
async def invalid_name(message: Message, state: FSMContext) -> None:
    await answer_new_message(message, texts.INVALID_NAME)


@router.message(Onboarding.entering_age, F.text)
async def save_age(message: Message, state: FSMContext, session: AsyncSession) -> None:
    raw_age = (message.text or "").strip()

    if not raw_age.isdigit():
        await answer_new_message(message, texts.INVALID_AGE)
        return

    age = int(raw_age)

    if age < MIN_AGE:
        await answer_new_message(message, texts.AGE_TOO_LOW)
        return

    if age > MAX_AGE:
        await answer_new_message(message, texts.AGE_TOO_HIGH)
        return

    user = await get_current_user(message, session)
    if user is None:
        await message.answer("Не удалось определить пользователя.")
        return

    await ProfileService(session).update(user, age=age)
    await state.set_state(Onboarding.choosing_gender)
    await answer_new_message(
        message,
        texts.ASK_GENDER,
        reply_markup=kb_gender(),
    )


@router.message(Onboarding.entering_age)
async def invalid_age(message: Message, state: FSMContext) -> None:
    await answer_new_message(message, texts.INVALID_AGE)


@router.callback_query(Onboarding.choosing_gender, F.data.startswith("ob:gender:"))
async def save_gender(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    value = (callback.data or "").removeprefix("ob:gender:")
    gender = enum_or_none(Gender, value)

    if gender is None:
        await callback.answer("Неизвестный вариант.", show_alert=True)
        return

    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    await ProfileService(session).set_gender(user, gender)
    await state.set_state(Onboarding.choosing_search_scope)
    await edit_callback_message(callback, texts.ASK_LOCATION_MODE, reply_markup=kb_search_scope())


@router.callback_query(Onboarding.choosing_search_scope, F.data.startswith("ob:scope:"))
async def save_search_scope(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    value = (callback.data or "").removeprefix("ob:scope:")
    scope = enum_or_none(SearchScope, value)

    if scope is None:
        await callback.answer("Неизвестный формат поиска.", show_alert=True)
        return

    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    profile_service = ProfileService(session)

    if scope == SearchScope.CITY:
        await profile_service.update(user, search_scope=scope)
        await state.set_state(Onboarding.entering_city)
        await edit_callback_message(callback, texts.ASK_CITY)
        return

    await profile_service.set_search_scope(user, scope)
    await _ask_interests(callback, state)


@router.message(Onboarding.entering_city, F.text)
async def save_city(message: Message, state: FSMContext, session: AsyncSession) -> None:
    city = _clean_text(message.text, max_len=64)

    if not _is_valid_city(city):
        await answer_new_message(message, texts.INVALID_CITY)
        return

    user = await get_current_user(message, session)
    if user is None:
        await message.answer("Не удалось определить пользователя.")
        return

    await ProfileService(session).set_search_scope(user, SearchScope.CITY, city=city)
    await _ask_interests_from_message(message, state)


@router.message(Onboarding.entering_city)
async def invalid_city(message: Message, state: FSMContext) -> None:
    await answer_new_message(message, texts.INVALID_CITY)
