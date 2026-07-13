from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import get_current_user
from app.bot.states.search import SearchState
from app.bot.texts import ru as texts

from app.bot.handlers.views import (
    get_current_card,
    show_current_candidate,
    show_match_success,
    show_next_candidate,
)

from app.bot.utils.messages import edit_callback_message
from app.db.models.report import ReportReason

from app.services.like_service import LikeService
from app.services.moderation_service import ModerationService
from app.services.notification_service import NotificationService

router = Router()


@router.callback_query(
    SearchState.searching,
    F.data.startswith("card:skip:")
)
async def skip_candidate(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    await show_next_candidate(
        callback,
        session,
        state,
    )

    await callback.answer()
    
@router.callback_query(
    SearchState.searching,
    F.data == "match:continue",
)
async def continue_search(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    await show_next_candidate(
        callback,
        session,
        state,
    )

    await callback.answer()


@router.callback_query(
    SearchState.searching,
    F.data.startswith("card:like:")
)
async def like_candidate(
    callback: CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    state: FSMContext,
):
    current = await get_current_card(state)
    
    if current is None:
        await edit_callback_message(
            callback,
            texts.NO_MORE_CANDIDATES,
        )
        return
    
    candidate_id = current["id"]

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

    like_service = LikeService(session)

    result = await like_service.send_like(
        from_user_id=current_user.id,
        to_user_id=candidate_id,
    )

    if result.is_match and result.matched_user:
        notification_service = NotificationService(bot)

        await notification_service.notify_match(
            user=result.matched_user,
            matched_with=current_user,
            common_interests=result.common_interests,
        )

        await show_match_success(
            callback,
            user=result.matched_user,
            common_interests=result.common_interests,
        )

        await callback.answer()
        return

    await show_next_candidate(
        callback,
        session,
        state,
    )


@router.callback_query(
    SearchState.searching,
    F.data.startswith("card:block:")
)
async def block_candidate(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    current = await get_current_card(state)
    
    if current is None:
        await edit_callback_message(
            callback,
            texts.NO_MORE_CANDIDATES,
        )
        return
    
    candidate_id = current["id"]

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

    moderation = ModerationService(session)

    await moderation.block_user(
        blocker_id=current_user.id,
        blocked_id=candidate_id,
    )

    await show_next_candidate(
        callback,
        session,
        state,
    )

    await callback.answer(
        texts.USER_BLOCKED,
    )


@router.callback_query(
    SearchState.searching,
    F.data.startswith("card:report:")
)
async def report_candidate(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    current = await get_current_card(state)
    
    if current is None:
        await edit_callback_message(
            callback,
            texts.NO_MORE_CANDIDATES,
        )
        return
    
    candidate_id = current["id"]

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

    moderation = ModerationService(session)

    await moderation.report_user(
        reporter_id=current_user.id,
        reported_id=candidate_id,
        reason=ReportReason.OTHER,
    )

    await show_next_candidate(
        callback,
        session,
        state,
    )

    await callback.answer(
        texts.REPORT_SENT,
    )