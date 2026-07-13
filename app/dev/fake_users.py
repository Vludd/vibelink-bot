from __future__ import annotations

import logging

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.interest import Interest
from app.db.models.user import User
from app.db.repositories import UserRepository
from app.dev.db import run_in_session
from app.services.dto.profile import ProfileData
from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)

fake = Faker("ru_RU")

CITIES = [
    "Алматы",
    "Астана",
    "Кокшетау",
    "Караганда",
    "Павлодар",
    "Шымкент",
    "Усть-Каменогорск",
    "Костанай",
    "Актобе",
    "Семей",
]


async def generate_fake_users(
    count: int = 50,
) -> None:
    """Generate fake completed profiles for development."""

    async def operation(session: AsyncSession) -> None:
        logger.info("Generating %s fake users...", count)

        interests = list(
            (
                await session.scalars(
                    select(Interest)
                )
            ).all()
        )

        if not interests:
            raise RuntimeError(
                "No interests found. Run `seed` first."
            )

        result = await session.scalar(
            select(func.max(User.telegram_id))
        )

        start_id = (result or 9_000_000_000) + 1

        profile_service = ProfileService(session)
        user_repo = UserRepository(session)

        for index in range(count):
            telegram_id = start_id + index
            username = f"{fake.user_name()}_{index}"

            user = await user_repo.get_or_create(
                telegram_id=telegram_id,
                telegram_username=username,
                with_interests=True,
            )

            # Загружаем relationship, чтобы избежать MissingGreenlet
            user = await user_repo.get_by_id(
                user.id,
                with_interests=True,
            )

            assert user is not None

            profile = ProfileData.random(
                interests=interests,
                cities=CITIES,
            )

            await profile_service.bootstrap_profile(
                user,
                profile,
            )

        await session.commit()

        logger.info(
            "Successfully generated %s fake users.",
            count,
        )

    await run_in_session(operation)