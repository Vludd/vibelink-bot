"""Клавиатуры для экрана мэтча (коннекта).

callback_data:
  match:open:<user_id>      ← открыть ЛС (ссылка на tg://user?id=…)
  match:greeting:<user_id>  ← скопировать готовое приветствие
  match:more                ← продолжить просматривать карточки
  match:hide:<user_id>      ← скрыть/убрать коннект из списка
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_match_actions(matched_user_id: int, telegram_username: str) -> InlineKeyboardMarkup:
    """Показывается обоим пользователям при взаимном коннекте."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Написать",
                url=f"https://t.me/{telegram_username}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="👋 Скопировать приветствие",
                callback_data=f"match:greeting:{matched_user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔎 Смотреть дальше",
                callback_data="match:more",
            ),
            InlineKeyboardButton(
                text="🚫 Скрыть коннект",
                callback_data=f"match:hide:{matched_user_id}",
            ),
        ],
    ])


def kb_copy_greeting(matched_user_id: int) -> InlineKeyboardMarkup:
    """После показа готового приветствия — позволяет сразу перейти в ЛС."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Скопировано — перейти в ЛС",
                callback_data=f"match:open:{matched_user_id}",
            ),
        ],
    ])