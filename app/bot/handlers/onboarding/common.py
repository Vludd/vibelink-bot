from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from typing import TypeVar

from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline.onboarding import GOAL_LABELS, GENDER_LABELS, SCOPE_LABELS
from app.db.models.interest import Interest
from app.db.models.user import Gender, Goal, SearchScope, User
from app.services.profile_service import ProfileService

EnumT = TypeVar("EnumT", bound=Enum)


def enum_or_none(enum_cls: type[EnumT], value: str | None) -> EnumT | None:
    if value is None:
        return None

    try:
        return enum_cls(value)
    except ValueError:
        return None


def enum_values(values: Iterable[Enum | str] | None) -> list[str]:
    if not values:
        return []

    result: list[str] = []
    for item in values:
        result.append(str(item.value if isinstance(item, Enum) else item))
    return result


def goal_set(values: Iterable[Enum | str] | None) -> set[Goal]:
    result: set[Goal] = set()

    for value in enum_values(values):
        goal = enum_or_none(Goal, value)
        if goal is not None:
            result.add(goal)

    return result


def interest_id_set(values: Iterable[int | str] | None) -> set[int]:
    result: set[int] = set()

    if not values:
        return result

    for value in values:
        try:
            result.add(int(value))
        except (TypeError, ValueError):
            continue

    return result


def label_goal(goal: Goal | str) -> str:
    parsed = enum_or_none(Goal, str(goal.value if isinstance(goal, Goal) else goal))
    return GOAL_LABELS.get(parsed, str(goal)) if parsed else str(goal)


def label_gender(gender: Gender | str | None) -> str:
    if gender is None:
        return "—"

    parsed = enum_or_none(Gender, str(gender.value if isinstance(gender, Gender) else gender))
    return GENDER_LABELS.get(parsed, str(gender)) if parsed else str(gender)


def label_search_scope(scope: SearchScope | str | None) -> str:
    if scope is None:
        return "—"

    raw_scope = str(scope.value if isinstance(scope, SearchScope) else scope)
    parsed = enum_or_none(SearchScope, raw_scope)
    return SCOPE_LABELS.get(parsed, str(scope)) if parsed else str(scope)


def selected_category_values(interests: Iterable[Interest]) -> set[str]:
    return {interest.category.value for interest in interests}


def profile_to_payload(user: User) -> dict:
    return {
        "name": user.name,
        "age": user.age if user.show_age else "скрыт",
        "city": user.city if user.show_city else "скрыт",
        "search_scope": label_search_scope(user.search_scope),
        "gender": label_gender(user.gender),
        "goals": [label_goal(goal) for goal in user.goals or []],
        "interests": [interest.name for interest in user.interests],
        "description": user.description,
    }


async def get_current_user(
    event: CallbackQuery | Message,
    session: AsyncSession,
    *,
    with_interests: bool = False,
) -> User | None:
    if event.from_user is None:
        return None

    profile_service = ProfileService(session)
    user = await profile_service.get_or_create(
        telegram_id=event.from_user.id,
        telegram_username=event.from_user.username,
    )
    user = await profile_service.sync_username(user, event.from_user.username)

    if with_interests:
        return await profile_service.get_by_telegram_id(
            event.from_user.id,
            with_interests=True,
        )

    return user
