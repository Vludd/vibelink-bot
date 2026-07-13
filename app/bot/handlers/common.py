from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline.match import kb_match_success
from app.bot.keyboards.inline.search import kb_candidate_card
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message

from app.db.models.user import User
from app.db.repositories import UserRepository

from app.bot.handlers.onboarding.common import profile_to_payload


async def get_current_card(
    state: FSMContext,
) -> dict | None:
    data = await state.get_data()

    cards = data.get("cards")
    index = data.get("index")

    if not cards or index is None:
        return None

    if index >= len(cards):
        return None

    return cards[index]


async def show_candidate(
    callback: CallbackQuery,
    user: User,
    match_percent: int,
    common_interests: list[str],
):
    """Display a candidate card."""

    payload = profile_to_payload(user)
    payload["match_percent"] = match_percent
    payload["common_interests"] = common_interests

    await edit_callback_message(
        callback,
        texts.candidate_card(payload),
        reply_markup=kb_candidate_card(user.id),
    )


async def show_current_candidate(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Show current candidate stored in FSM."""

    current = await get_current_card(state)

    user_repo = UserRepository(session)

    if current is None:
        await edit_callback_message(
            callback,
            texts.NO_MORE_CANDIDATES,
        )
        return
    
    user = await user_repo.get_by_id(
        current["id"],
        with_interests=True,
    )

    if user is None:
        await show_next_candidate(
            callback,
            session,
            state,
        )
        return

    await show_candidate(
        callback,
        user=user,
        match_percent=current["match_percent"],
        common_interests=current["common_interests"],
    )


async def show_next_candidate(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Advance to the next candidate."""

    data = await state.get_data()

    cards = data["cards"]
    index = data["index"] + 1

    if index >= len(cards):
        await state.clear()

        await edit_callback_message(
            callback,
            texts.NO_MORE_CANDIDATES,
        )
        return

    await state.update_data(index=index)

    await show_current_candidate(
        callback,
        session,
        state,
    )
    
async def show_match_success(
    callback: CallbackQuery,
    user: User,
    common_interests: list[str],
) -> None:
    if user.telegram_username is None:
        raise ValueError(
            "Matched user has no telegram_username."
        )

    payload = profile_to_payload(user)
    payload["common_interests"] = common_interests

    await edit_callback_message(
        callback,
        texts.match_created(
            matched_user=payload,
            common_interests=common_interests,
        ),
        reply_markup=kb_match_success(
            username=user.telegram_username,
        ),
    )
