from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.common import show_current_candidate
from app.bot.keyboards.inline.search import kb_search_goal
from app.bot.states.search import SearchState
from app.bot.texts import ru as texts
from app.bot.handlers.onboarding.common import get_current_user
from app.bot.utils.messages import edit_callback_message
from app.db.models.user import Goal
from app.services.matching_service import MatchingService

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "menu:search")
async def search_menu(
    callback: CallbackQuery,
):
    await edit_callback_message(
        callback,
        texts.SEARCH_MODE_SELECT,
        reply_markup=kb_search_goal(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("search:goal:"))
async def search_goal(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    
    assert callback.data is not None
    goal_value = callback.data.split(":")[-1]

    try:
        goal = None if goal_value == "any" else Goal(goal_value)
    except ValueError:
        await callback.answer(
            texts.INVALID_SEARCH_MODE,
            show_alert=True,
        )
        return

    current_user = await get_current_user(callback, session, with_interests=True)

    if current_user is None:
        logger.warning("Current user not found for callback: %s", callback.data)
        await callback.answer(texts.USER_IS_NOT_FOUND, show_alert=True)
        return
    
    matching_service = MatchingService(session)
    
    candidates = await matching_service.get_candidates(
        current_user,
        goal=goal,
    )

    if not candidates:
        logger.info(
            "No candidates found for user %s",
            current_user.telegram_id,
        )
        await edit_callback_message(
            callback,
            texts.NO_CANDIDATES,
        )
        await callback.answer()
        return

    await state.set_state(SearchState.searching)

    await state.update_data(
        goal=goal_value,
        cards=[
            {
                "id": candidate.user.id,
                "match_percent": candidate.match_percent,
                "common_interests": candidate.common_interests,
            }
            for candidate in candidates
        ],
        index=0,
    )
    
    await show_current_candidate(
        callback,
        session,
        state,
    )
    
    await callback.answer()
