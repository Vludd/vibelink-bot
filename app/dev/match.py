from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories import UserRepository
from app.dev.db import run_in_session
from app.services.like_service import LikeService

logger = logging.getLogger(__name__)


async def generate_matches(
    telegram_id: int,
    *,
    count: int = 20,
    mutual: bool = False,
) -> None:
    """Generate likes (or mutual matches) for a user."""

    async def operation(session: AsyncSession) -> None:
        user_repo = UserRepository(session)
        like_service = LikeService(session)

        target = await user_repo.get_by_telegram_id(
            telegram_id,
            with_interests=True,
        )

        if target is None:
            raise RuntimeError(
                f"User with telegram_id={telegram_id} not found."
            )

        fake_users = list(
            (
                await session.scalars(
                    select(User)
                    .where(
                        User.id != target.id,
                        User.is_profile_complete.is_(True),
                        User.is_hidden.is_(False),
                        User.is_banned.is_(False),
                    )
                    .limit(count)
                )
            ).all()
        )

        likes = 0
        matches = 0

        for fake in fake_users:
            await like_service.send_like(
                from_user_id=fake.id,
                to_user_id=target.id,
            )
            likes += 1

            if mutual:
                result = await like_service.create_match(
                    fake.id,
                    target.id,
                )

                if result.is_match:
                    matches += 1
            else:
                await like_service.send_like(
                    fake.id,
                    target.id,
                )

        await session.commit()

        logger.info(
            "Generated %s likes and %s matches.",
            likes,
            matches,
        )

    await run_in_session(operation)