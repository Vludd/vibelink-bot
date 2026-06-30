from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.interest import Interest, InterestCategory


class InterestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, interest_id: int) -> Interest | None:
        return await self.session.get(Interest, interest_id)

    async def get_by_ids(self, interest_ids: list[int]) -> list[Interest]:
        """Used in onboarding to resolve picked tag-buttons into Interest rows
        for UserRepository.set_interests()."""
        if not interest_ids:
            return []
        stmt = select(Interest).where(Interest.id.in_(interest_ids))
        return list((await self.session.scalars(stmt)).all())

    async def list_by_category(self, category: InterestCategory) -> list[Interest]:
        """Powers the tag keyboard shown after a category is picked
        (e.g. category=GAMES -> Minecraft, CS2, Dota 2, ...)."""
        stmt = (
            select(Interest)
            .where(Interest.category == category)
            .order_by(Interest.name)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_categories(self) -> list[InterestCategory]:
        """Distinct categories present in the table, for the first-level
        category keyboard. Falls back to the full enum if the table is empty."""
        stmt = select(Interest.category).distinct()
        categories = set((await self.session.scalars(stmt)).all())
        return list(categories) if categories else list(InterestCategory)

    async def get_or_create(self, category: InterestCategory, name: str) -> Interest:
        """Idempotent creation — useful for seeding and for admin-added tags."""
        stmt = (
            pg_insert(Interest)
            .values(category=category, name=name)
            .on_conflict_do_nothing(constraint="uq_interest_category_name")
            .returning(Interest)
        )
        result = await self.session.execute(stmt)
        interest = result.scalar_one_or_none()
        if interest is None:
            interest = await self.get_by_category_and_name(category, name)
        return interest

    async def get_by_category_and_name(
        self, category: InterestCategory, name: str
    ) -> Interest | None:
        stmt = select(Interest).where(
            Interest.category == category, Interest.name == name
        )
        return await self.session.scalar(stmt)