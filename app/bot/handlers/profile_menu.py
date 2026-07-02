from __future__ import annotations

from enum import Enum
from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline.profile import kb_profile_menu
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.services.profile_service import ProfileService

router = Router(name="profile_menu")


GOAL_LABELS: dict[str, str] = {
    "friend": "👥 Друга",
    "relationship": "💜 Отношения",
    "teammate": "🎮 Тиммейта",
    "business": "💼 Бизнес-контакт",
    "project": "🧑‍💻 Проект",
    "chat": "💬 Общение",
}

SEARCH_SCOPE_LABELS: dict[str, str] = {
    "city": "📍 В моём городе",
    "online": "🌍 Онлайн",
    "country": "🇰🇿 По стране / СНГ",
}


def enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def format_enum(value: Any) -> str:
    if value is None:
        return "—"

    raw = enum_value(value)
    return raw.replace("_", " ")


def format_goals(goals: list[Any] | None) -> list[str]:
    if not goals:
        return []

    result: list[str] = []

    for goal in goals:
        raw = enum_value(goal)
        result.append(GOAL_LABELS.get(raw, raw))

    return result


def format_search_scope(search_scope: Any) -> str:
    if search_scope is None:
        return "—"

    raw = enum_value(search_scope)
    return SEARCH_SCOPE_LABELS.get(raw, raw)


@router.callback_query(F.data == "menu:profile")
async def show_profile(callback: CallbackQuery, session: AsyncSession) -> None:
    profile_service = ProfileService(session)
    user = await profile_service.get_by_telegram_id(callback.from_user.id)

    if user is None:
        await edit_callback_message(
            callback,
            texts.PROFILE_REQUIRED,
        )
        return

    if not user.is_profile_complete:
        await edit_callback_message(
            callback,
            "👤 <b>Мой профиль</b>\n\n"
            "Профиль ещё не заполнен.\n\n"
            "Нужно пройти короткую анкету, чтобы я мог подбирать людей по интересам.",
            reply_markup=kb_profile_menu(is_hidden=user.is_hidden),
        )
        return

    await edit_callback_message(
        callback,
        texts.profile_view(
            {
                "name": user.name,
                "age": user.age if user.show_age else "скрыт",
                "city": user.city if user.show_city else "скрыт",
                "search_scope": format_search_scope(user.search_scope),
                "gender": format_enum(user.gender),
                "goals": format_goals(user.goals),
                "interests": [],  # позже - через eager loading
                "description": user.description,
            }
        ),
        reply_markup=kb_profile_menu(is_hidden=user.is_hidden),
    )