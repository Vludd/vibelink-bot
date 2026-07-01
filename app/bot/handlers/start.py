# app/bot/handlers/start.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.inline.profile import kb_main_menu
from app.bot.texts import ru as texts

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    username = message.from_user.username if message.from_user else None

    await message.answer(
        texts.start_text(username),
        reply_markup=kb_main_menu(),
    )
