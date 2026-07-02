from __future__ import annotations

import logging
from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

logger = logging.getLogger(__name__)


def _is_message_not_modified(error: TelegramBadRequest) -> bool:
    return "message is not modified" in str(error).lower()


async def edit_callback_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Edit message that contains inline button.

    Best for:
    - menu navigation
    - profile screens
    - search cards
    - onboarding steps via inline buttons
    """

    if not isinstance(callback.message, Message):
        await callback.answer("Сообщение недоступно для редактирования.", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as error:
        if _is_message_not_modified(error):
            await callback.answer()
            return

        logger.warning("Failed to edit callback message: %s", error)

        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
        )

    await callback.answer()


async def answer_new_message(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message:
    """
    Force sending new message.

    Best for:
    - /start
    - match notification
    - important errors
    - messages to another user
    """

    return await message.answer(
        text=text,
        reply_markup=reply_markup,
    )


async def answer_or_replace_last_bot_message(
    message: Message,
    state: FSMContext,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    state_key: str = "last_bot_message_id",
) -> Message | None:
    """
    For FSM/user text input.

    Telegram bot cannot edit user's message.
    But we can remember previous bot message_id and edit that.

    Flow:
    - if last bot message exists in FSM state -> edit it
    - otherwise -> send new message
    - save new/edited message id into FSM state
    """

    data = await state.get_data()
    last_bot_message_id = data.get(state_key)

    if last_bot_message_id:
        try:
            edited_message = await message.bot.edit_message_text( # type: ignore
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                text=text,
                reply_markup=reply_markup,
            )

            if isinstance(edited_message, Message):
                await state.update_data({state_key: edited_message.message_id})
                return edited_message

            return None

        except TelegramBadRequest as error:
            if _is_message_not_modified(error):
                return None

            logger.warning("Failed to edit last bot message: %s", error)

    sent_message = await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await state.update_data({state_key: sent_message.message_id})
    return sent_message


async def remember_bot_message(
    state: FSMContext,
    message: Message,
    state_key: str = "last_bot_message_id",
) -> None:
    await state.update_data({state_key: message.message_id})


async def clear_remembered_bot_message(
    state: FSMContext,
    state_key: str = "last_bot_message_id",
) -> None:
    await state.update_data({state_key: None})