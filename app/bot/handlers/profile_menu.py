from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.views import show_main_menu, show_profile
from app.bot.keyboards.inline.profile import kb_profile_menu
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.services.profile_service import ProfileService

router = Router(name="profile_menu")


async def get_profile(
    session: AsyncSession,
    telegram_id: int,
    *,
    with_interests: bool = False,
):
    return await ProfileService(session).get_by_telegram_id(
        telegram_id,
        with_interests=with_interests,
    )


@router.callback_query(F.data == "menu:back")
async def back_to_main_menu(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    user = await get_profile(
        session,
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    await show_main_menu(
        callback,
        user,
    )

    await callback.answer()
    
@router.callback_query(
    F.data.in_(
        {
            "menu:toggle_hidden",
            "prof:toggle_hidden",
        }
    )
)
async def toggle_hidden(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    from_profile = callback.data == "prof:toggle_hidden"

    profile_service = ProfileService(session)

    user = await get_profile(
        session,
        callback.from_user.id,
        with_interests=True,
    )

    if user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    user = await profile_service.toggle_hidden(user)

    if from_profile:
        await show_profile(
            callback,
            user,
        )
    else:
        await show_main_menu(
            callback,
            user,
        )

    await callback.answer()


@router.callback_query(F.data == "menu:profile")
async def show_profile_handler(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    user = await get_profile(
        session,
        callback.from_user.id,
        with_interests=True,
    )

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
            reply_markup=kb_profile_menu(
                is_hidden=user.is_hidden,
                is_complete=False,
            ),
        )
        return

    await show_profile(
        callback,
        user,
    )
