"""Клавиатуры профиля, главного меню и модерации.

callback_data:
  menu:<action>             ← главное меню
  prof:<action>             ← меню профиля / редактирования
  report:<reason>:<uid>     ← причина жалобы
  block:confirm:<uid>       ← подтверждение блокировки
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.report import ReportReason


REPORT_REASON_LABELS: dict[ReportReason, str] = {
    ReportReason.SPAM:                 "📩 Спам",
    ReportReason.INSULTS:              "🤬 Оскорбления",
    ReportReason.FAKE_PROFILE:         "🎭 Фейковый профиль",
    ReportReason.INAPPROPRIATE_CONTENT:"🔞 Неподходящий контент",
    ReportReason.FRAUD:                "💸 Мошенничество",
    ReportReason.OTHER:                "❓ Другое",
}


# ─────────────────────────── главное меню ─────────────────────────────────

def kb_main_menu(is_hidden: bool = False) -> InlineKeyboardMarkup:
    hidden_label = "👁 Показать меня в поиске" if is_hidden else "⏸ Скрыть меня из поиска"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Искать людей",    callback_data="menu:search")],
        [InlineKeyboardButton(text="💌 Мои коннекты",    callback_data="menu:matches")],
        [InlineKeyboardButton(text="👤 Мой профиль",     callback_data="menu:profile")],
        [InlineKeyboardButton(text="⚙️ Фильтры",         callback_data="menu:filters")],
        [InlineKeyboardButton(text=hidden_label,         callback_data="menu:toggle_hidden")],
    ])


# ─────────────────────────── профиль ──────────────────────────────────────

def kb_profile_menu(is_hidden: bool = False, is_complete: bool = True) -> InlineKeyboardMarkup:
    hidden_label = "👁 Показать в поиске" if is_hidden else "⏸ Скрыть из поиска"

    if not is_complete:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Заполнить профиль", callback_data="ob:start")],
            [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="ob:how")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")],
        ])

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Посмотреть анкету", callback_data="prof:view")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="prof:edit")],
        [InlineKeyboardButton(text=hidden_label, callback_data="prof:toggle_hidden")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")],
    ])


def kb_profile_edit() -> InlineKeyboardMarkup:
    """Меню редактирования отдельных полей профиля."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Имя",          callback_data="prof:edit:name")],
        [InlineKeyboardButton(text="🎂 Возраст",      callback_data="prof:edit:age")],
        [InlineKeyboardButton(text="📍 Город / зона", callback_data="prof:edit:scope")],
        [InlineKeyboardButton(text="🎯 Цели",         callback_data="prof:edit:goals")],
        [InlineKeyboardButton(text="🏷 Интересы",     callback_data="prof:edit:interests")],
        [InlineKeyboardButton(text="📄 Описание",     callback_data="prof:edit:description")],
        [InlineKeyboardButton(text="📸 Фото",         callback_data="prof:edit:photo")],
        [InlineKeyboardButton(text="🔒 Приватность",  callback_data="prof:edit:privacy")],
        [InlineKeyboardButton(text="◀️ Назад",        callback_data="prof:back")],
    ])


def kb_hidden_toggle(is_hidden: bool) -> InlineKeyboardMarkup:
    """Подтверждение смены видимости профиля."""
    action_text = "👁 Да, показать меня" if is_hidden else "⏸ Да, скрыть меня"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=action_text,  callback_data="prof:hidden:confirm")],
        [InlineKeyboardButton(text="◀️ Отмена",  callback_data="prof:hidden:cancel")],
    ])


# ─────────────────────────── жалоба / блок ────────────────────────────────

def kb_report_reason(reported_user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for reason, label in REPORT_REASON_LABELS.items():
        builder.button(
            text=label,
            callback_data=f"report:{reason.value}:{reported_user_id}",
        )
    builder.button(text="◀️ Отмена", callback_data="report:cancel")
    builder.adjust(1)
    return builder.as_markup()


def kb_block_confirm(blocked_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Да, заблокировать", callback_data=f"block:confirm:{blocked_user_id}"),
            InlineKeyboardButton(text="◀️ Отмена",            callback_data="block:cancel"),
        ]
    ])