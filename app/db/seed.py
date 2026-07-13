from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.interest import (
    Interest,
    InterestCategory,
)

DEFAULT_INTERESTS: dict[InterestCategory, list[str]] = {
    InterestCategory.IT: [
        "Python",
        "Go",
        "Rust",
        "Java",
        "C#",
        "JavaScript",
        "DevOps",
        "Cybersecurity",
    ],
    InterestCategory.GAMES: [
        "CS2",
        "Dota 2",
        "Minecraft",
        "Valorant",
        "League of Legends",
    ],
    InterestCategory.MUSIC: [
        "Rock",
        "Hip-Hop",
        "EDM",
        "Jazz",
        "Classical",
    ],
}


async def seed_default_interests(
    session: AsyncSession,
) -> None:
    """Populate default interests if the table is empty."""

    exists = await session.scalar(select(Interest.id).limit(1))

    if exists:
        return

    for category, names in DEFAULT_INTERESTS.items():
        for name in names:
            session.add(
                Interest(
                    category=category,
                    name=name,
                )
            )

    await session.flush()