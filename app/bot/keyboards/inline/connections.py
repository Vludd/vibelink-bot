from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.user import User


def kb_connections_list(
    connections: list[User],
) -> InlineKeyboardMarkup:
    """Список взаимных коннектов пользователя."""

    builder = InlineKeyboardBuilder()

    for user in connections:
        builder.button(
            text=f"👤 {user.name}",
            callback_data=f"connections:view:{user.id}",
        )

    builder.button(
        text="◀️ Назад",
        callback_data="menu:back",
    )

    builder.adjust(1)

    return builder.as_markup()


def kb_connection(
    user_id: int,
    telegram_username: str,
) -> InlineKeyboardMarkup:
    """Карточка конкретного коннекта."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать",
                    url=f"https://t.me/{telegram_username}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👋 Скопировать приветствие",
                    callback_data=f"connections:greeting:{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ К списку",
                    callback_data="connections:back",
                ),
            ],
        ]
    )
    
    
def kb_connection_greeting(
    telegram_username: str,
    user_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать",
                    url=f"https://t.me/{telegram_username}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"connections:view:{user_id}",
                )
            ],
        ]
    )


def kb_connections_empty() -> InlineKeyboardMarkup:
    """Экран, когда взаимных коннектов пока нет."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Искать людей",
                    callback_data="menu:search",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="menu:back",
                ),
            ],
        ]
    )