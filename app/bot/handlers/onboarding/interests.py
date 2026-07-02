from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.onboarding.common import enum_or_none, interest_id_set
from app.bot.keyboards.inline.onboarding import (
    CATEGORY_LABELS,
    kb_interest_categories,
    kb_interest_tags,
)
from app.bot.states.onboarding import Onboarding
from app.bot.texts import ru as texts
from app.bot.utils.messages import edit_callback_message
from app.db.models.interest import InterestCategory
from app.services.profile_service import ProfileService

router = Router(name="onboarding_interests")

DEFAULT_INTERESTS: dict[InterestCategory, tuple[str, ...]] = {
    InterestCategory.GAMES: (
        "Minecraft",
        "CS2",
        "Dota 2",
        "Valorant",
        "GTA",
        "Roblox",
        "MMORPG",
        "Кооп-игры",
        "Инди-игры",
    ),
    InterestCategory.IT: (
        "Backend",
        "Frontend",
        "Cybersecurity",
        "AI/ML",
        "DevOps",
        "GameDev",
        "Mobile",
        "Open Source",
    ),
    InterestCategory.MOVIES: (
        "Кино",
        "Сериалы",
        "Аниме",
        "Фантастика",
        "Комедии",
        "Документалки",
    ),
    InterestCategory.MUSIC: (
        "Рок",
        "Поп",
        "Хип-хоп",
        "Электроника",
        "Инди",
        "K-pop",
        "Музыкальные концерты",
    ),
    InterestCategory.BOOKS: (
        "Фантастика",
        "Фэнтези",
        "Психология",
        "Бизнес-книги",
        "Манга",
        "Нон-фикшн",
    ),
    InterestCategory.SPORT: (
        "Футбол",
        "Баскетбол",
        "Волейбол",
        "Тренажёрный зал",
        "Бег",
        "Плавание",
        "Единоборства",
    ),
    InterestCategory.BUSINESS: (
        "Стартапы",
        "Маркетинг",
        "Продажи",
        "Инвестиции",
        "Нетворкинг",
        "Фриланс",
    ),
    InterestCategory.CREATIVITY: (
        "Дизайн",
        "Фото",
        "Видео",
        "Рисование",
        "Музыка",
        "3D",
        "Писательство",
    ),
    InterestCategory.SELF_GROWTH: (
        "Английский",
        "Продуктивность",
        "Карьера",
        "Психология",
        "Финансы",
        "Здоровые привычки",
    ),
}


async def _ensure_default_interests(
    profile_service: ProfileService,
    category: InterestCategory,
) -> None:
    existing = await profile_service.interest_repo.list_by_category(category)
    if existing:
        return

    for name in DEFAULT_INTERESTS.get(category, ()): 
        await profile_service.interest_repo.get_or_create(category, name)


async def _show_category_tags(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    category: InterestCategory,
) -> None:
    profile_service = ProfileService(session)
    await _ensure_default_interests(profile_service, category)

    interests = await profile_service.interest_repo.list_by_category(category)
    data = await state.get_data()
    selected_ids = interest_id_set(data.get("selected_interest_ids"))

    await state.set_state(Onboarding.choosing_interest_tags)
    await state.update_data(current_interest_category=category.value)

    category_label = CATEGORY_LABELS.get(category, category.value)
    text = f"🏷 <b>{category_label}</b>\n\n{texts.ASK_INTERESTS}"

    await edit_callback_message(
        callback,
        text,
        reply_markup=kb_interest_tags(interests, selected_ids, category),
    )


@router.callback_query(Onboarding.choosing_interest_categories, F.data.startswith("ob:cat:"))
async def open_interest_category(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    value = (callback.data or "").removeprefix("ob:cat:")
    category = enum_or_none(InterestCategory, value)

    if category is None:
        await callback.answer("Неизвестная категория.", show_alert=True)
        return

    await _show_category_tags(callback, state, session, category)


@router.callback_query(Onboarding.choosing_interest_tags, F.data.startswith("ob:tag:"))
async def toggle_interest_tag(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    raw_id = (callback.data or "").removeprefix("ob:tag:")

    try:
        interest_id = int(raw_id)
    except ValueError:
        await callback.answer("Неизвестный интерес.", show_alert=True)
        return

    data = await state.get_data()
    selected_ids = interest_id_set(data.get("selected_interest_ids"))
    category = enum_or_none(InterestCategory, data.get("current_interest_category"))

    if interest_id in selected_ids:
        selected_ids.remove(interest_id)
    else:
        selected_ids.add(interest_id)

    if category is None:
        await callback.answer("Категория потерялась, вернись назад.", show_alert=True)
        return

    selected_category_values = set(data.get("selected_category_values") or [])
    profile_service = ProfileService(session)
    category_interests = await profile_service.interest_repo.list_by_category(category)
    category_interest_ids = {interest.id for interest in category_interests}

    if selected_ids & category_interest_ids:
        selected_category_values.add(category.value)
    else:
        selected_category_values.discard(category.value)

    await state.update_data(
        selected_interest_ids=list(selected_ids),
        selected_category_values=list(selected_category_values),
    )

    await _show_category_tags(callback, state, session, category)


@router.callback_query(Onboarding.choosing_interest_tags, F.data == "ob:back:cats")
async def back_to_interest_categories(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected_category_values = set(data.get("selected_category_values") or [])

    selected_categories = {
        category
        for value in selected_category_values
        if (category := enum_or_none(InterestCategory, value)) is not None
    }

    await state.set_state(Onboarding.choosing_interest_categories)
    await state.update_data(selected_category_values=list(selected_category_values))
    await edit_callback_message(
        callback,
        texts.ASK_INTEREST_CATEGORIES,
        reply_markup=kb_interest_categories(selected_categories),
    )


@router.callback_query(
    Onboarding.choosing_interest_categories,
    F.data == "ob:done:interests",
)
@router.callback_query(Onboarding.choosing_interest_tags, F.data.startswith("ob:done:tags"))
async def save_interests(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()
    selected_ids = interest_id_set(data.get("selected_interest_ids"))

    if not selected_ids:
        await callback.answer(texts.NEED_SELECT_INTEREST, show_alert=True)
        return

    if callback.from_user is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    profile_service = ProfileService(session)
    user = await profile_service.get_by_telegram_id(
        callback.from_user.id,
        with_interests=True,
    )

    if user is None:
        await callback.answer("Не удалось найти профиль.", show_alert=True)
        return

    await profile_service.set_interests_by_ids(user, list(selected_ids))
    await state.set_state(Onboarding.entering_description)
    await edit_callback_message(callback, texts.ASK_DESCRIPTION)
