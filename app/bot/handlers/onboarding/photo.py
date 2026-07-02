from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import get_current_user
from app.bot.keyboards.inline.onboarding import kb_photo_choice, kb_privacy
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import answer_new_message, edit_callback_message
from app.services.profile_service import ProfileService

router = Router(name="onboarding_photo")


async def _ask_privacy_from_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Onboarding.choosing_privacy)
    await state.update_data(show_age=True, show_city=True)
    await edit_callback_message(callback, texts.ASK_PRIVACY, reply_markup=kb_privacy())


async def _ask_privacy_from_message(message: Message, state: FSMContext) -> None:
    await state.set_state(Onboarding.choosing_privacy)
    await state.update_data(show_age=True, show_city=True)
    await answer_new_message(
        message,
        texts.ASK_PRIVACY,
        reply_markup=kb_privacy(),
    )


@router.callback_query(Onboarding.choosing_photo, F.data == "ob:photo:add")
async def ask_photo_upload(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Onboarding.waiting_photo)
    await edit_callback_message(
        callback,
        texts.ASK_PHOTO_UPLOAD,
        reply_markup=kb_photo_choice(),
    )


@router.callback_query(Onboarding.choosing_photo, F.data == "ob:photo:skip")
@router.callback_query(Onboarding.waiting_photo, F.data == "ob:photo:skip")
async def skip_photo(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    user = await get_current_user(callback, session)
    if user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    await ProfileService(session).update(user, photo_file_id=None)
    await _ask_privacy_from_callback(callback, state)


@router.message(Onboarding.waiting_photo, F.photo)
async def save_photo(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.photo:
        await answer_new_message(
            message,
            texts.INVALID_PHOTO,
            reply_markup=kb_photo_choice(),
        )
        return

    user = await get_current_user(message, session)
    if user is None:
        await message.answer("Не удалось определить пользователя.")
        return

    photo_file_id = message.photo[-1].file_id
    await ProfileService(session).update(user, photo_file_id=photo_file_id)
    await _ask_privacy_from_message(message, state)


@router.message(Onboarding.waiting_photo)
async def invalid_photo(message: Message, state: FSMContext) -> None:
    await answer_new_message(
        message,
        texts.INVALID_PHOTO,
        reply_markup=kb_photo_choice(),
    )
