from aiogram import F, Router
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.views import (
    show_connection as show_connection_view,
    show_connection_greeting,
    show_connections_list,
)

from app.bot.handlers.onboarding.common import get_current_user
from app.bot.keyboards.inline.profile import kb_main_menu
from app.bot.texts import ru as texts

from app.bot.utils.messages import edit_callback_message
from app.db.models.user import User
from app.services.greeting_service import GreetingService
from app.services.like_service import LikeService

router = Router(name="connections")


@router.callback_query(F.data == "menu:connections")
async def show_connections(
    callback: CallbackQuery,
    session: AsyncSession,
):
    current_user = await get_current_user(
        callback,
        session,
    )

    if current_user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    await show_connections_list(
        callback,
        session,
        current_user,
    )


@router.callback_query(F.data.startswith("connections:view:"))
async def show_connection(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Open a single connection."""

    current_user = await get_current_user(
        callback,
        session,
    )

    if current_user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    assert callback.data is not None
    connection_id = int(
        callback.data.rsplit(":", 1)[1]
    )

    like_service = LikeService(session)

    user = await like_service.get_match(
        current_user.id,
        connection_id,
        with_interests=True,
    )

    if user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    await show_connection_view(
        callback,
        user,
    )


@router.callback_query(F.data == "connections:back")
async def back_to_connections(
    callback: CallbackQuery,
    session: AsyncSession,
):
    current_user = await get_current_user(
        callback,
        session,
    )

    if current_user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    await show_connections_list(
        callback,
        session,
        current_user,
    )

    await callback.answer()

@router.callback_query(
    F.data.startswith("connections:greeting:")
)
async def connection_greeting(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Show a ready-to-send greeting for a connection."""

    current_user = await get_current_user(
        callback,
        session,
        with_interests=True,
    )

    if current_user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return

    assert callback.data is not None
    connection_id = int(
        callback.data.rsplit(":", 1)[1]
    )

    like_service = LikeService(session)

    user = await like_service.get_match(
        current_user.id,
        connection_id,
        with_interests=True,
    )

    if user is None:
        await callback.answer(
            texts.USER_IS_NOT_FOUND,
            show_alert=True,
        )
        return
    
    viewer_interest_ids = {
        interest.id
        for interest in current_user.interests
    }

    common_interests = [
        interest.name
        for interest in user.interests
        if interest.id in viewer_interest_ids
    ]

    greeting = GreetingService().build(
        common_interests=common_interests
    )

    await show_connection_greeting(
        callback,
        user=user,
        greeting=greeting,
    )

    await callback.answer()
    
async def show_main_menu(
    callback: CallbackQuery,
    user: User,
) -> None:
    await edit_callback_message(
        callback,
        texts.MAIN_MENU,
        reply_markup=kb_main_menu(
            is_hidden=user.is_hidden,
        ),
    )