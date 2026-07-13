"""Клавиатуры для поиска и карточек кандидатов.

callback_data:
  search:goal:<value>        ← выбор цели перед поиском
  card:like:<user_id>        ← лайк карточки
  card:skip:<user_id>        ← пропустить
  card:report:<user_id>      ← открыть меню жалобы
  card:block:<user_id>       ← заблокировать (подтверждение)
  filter:<field>:<value>     ← применить фильтр
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.user import Goal
from app.bot.keyboards.inline.onboarding import GOAL_LABELS


def kb_search_goal() -> InlineKeyboardMarkup:
    """Выбор режима поиска перед показом карточек."""
    builder = InlineKeyboardBuilder()

    for goal, label in GOAL_LABELS.items():
        builder.button(
            text=label,
            callback_data=f"search:goal:{goal.value}",
        )

    builder.button(
        text="🎲 Любого по интересам",
        callback_data="search:goal:any",
    )

    builder.button(
        text="◀️ Назад",
        callback_data="menu:back",
    )

    builder.adjust(1)

    return builder.as_markup()


def kb_candidate_card(candidate_id: int) -> InlineKeyboardMarkup:
    """Кнопки под карточкой кандидата."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❤️ Нравится", callback_data=f"card:like:{candidate_id}"),
            InlineKeyboardButton(text="➡️ Пропустить", callback_data=f"card:skip:{candidate_id}"),
        ],
        [
            InlineKeyboardButton(text="🚩 Пожаловаться", callback_data=f"card:report:{candidate_id}"),
            InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"card:block:{candidate_id}"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data=f"search:menu"),
        ],
    ])


def kb_search_filters(
    *,
    goal: Goal | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    online_only: bool = False,
) -> InlineKeyboardMarkup:
    """Меню фильтров. Показывает текущие значения и позволяет их сбросить."""
    builder = InlineKeyboardBuilder()

    goal_label = GOAL_LABELS.get(goal, "Любой") if goal else "Любой"
    builder.button(text=f"🎯 Цель: {goal_label}", callback_data="filter:goal:pick")

    age_label = f"{min_age or '?'}–{max_age or '?'}"
    builder.button(text=f"🎂 Возраст: {age_label}", callback_data="filter:age:pick")

    scope_label = "Онлайн" if online_only else "Все"
    builder.button(text=f"🌍 Формат: {scope_label}", callback_data="filter:online:toggle")

    builder.button(text="🔄 Сбросить фильтры", callback_data="filter:reset")
    builder.button(text="✅ Применить", callback_data="filter:apply")
    builder.adjust(1)
    return builder.as_markup()