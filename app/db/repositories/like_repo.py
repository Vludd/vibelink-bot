from sqlalchemy import exists, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.models.like import Like


class LikeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_like(self, from_user_id: int, to_user_id: int) -> Like:
        """Idempotent - pressing 'Like' twice on the same card is a no-op,
        not an IntegrityError."""
        stmt = (
            pg_insert(Like)
            .values(from_user_id=from_user_id, to_user_id=to_user_id)
            .on_conflict_do_nothing(constraint="uq_like_from_to")
            .returning(Like)
        )
        
        result = await self.session.execute(stmt)
        like = result.scalar_one_or_none()

        if like is not None:
            return like

        existing_like = await self.get(from_user_id, to_user_id)
        if existing_like is None:
            raise RuntimeError(
                f"Like was not inserted and existing like was not found: "
                f"from_user_id={from_user_id}, to_user_id={to_user_id}"
            )

        return existing_like

    async def get(self, from_user_id: int, to_user_id: int) -> Like | None:
        stmt = (
            select(Like)
            .where(Like.from_user_id == from_user_id, Like.to_user_id == to_user_id)
        )
        
        return await self.session.scalar(stmt)

    async def has_liked(self, from_user_id: int, to_user_id: int) -> bool:
        stmt = (
            select(
                exists()
                .where(Like.from_user_id == from_user_id, Like.to_user_id == to_user_id)
            )
        )

        return bool(await self.session.scalar(stmt))

    async def is_mutual(self, user_a_id: int, user_b_id: int) -> bool:
        """True once both A->B and B->A rows exist - this *is* the match,
        there's no separate Match row/table."""
        stmt = (
            select(
                exists()
                .where(Like.from_user_id == user_a_id, Like.to_user_id == user_b_id)
                & exists().where(
                    Like.from_user_id == user_b_id, Like.to_user_id == user_a_id
                )
            )
        )

        return bool(await self.session.scalar(stmt))

    async def get_sent_ids(self, user_id: int) -> set[int]:
        """IDs already liked by user_id - used by matching_service to keep
        them out of the candidate pool (no point re-showing a liked card)."""
        stmt = (
            select(Like.to_user_id)
            .where(Like.from_user_id == user_id)
        )
        
        return set((await self.session.scalars(stmt)).all())

    async def get_received_ids(self, user_id: int) -> set[int]:
        """IDs who liked user_id - powers 'My likes'."""
        stmt = (
            select(Like.from_user_id)
            .where(Like.to_user_id == user_id)
        )
        
        return set((await self.session.scalars(stmt)).all())

    async def get_match_ids(self, user_id: int) -> set[int]:
        """IDs with a mutual like - powers connections list."""
        outgoing = aliased(Like)
        incoming = aliased(Like)

        stmt = (
            select(outgoing.to_user_id)
            .join(
                incoming,
                (incoming.from_user_id == outgoing.to_user_id)
                & (incoming.to_user_id == outgoing.from_user_id),
            )
            .where(outgoing.from_user_id == user_id)
        )
        
        return set((await self.session.scalars(stmt)).all())

    async def remove_like(self, from_user_id: int, to_user_id: int) -> bool:
        """Used for an 'unlike' action."""
        like = await self.get(from_user_id, to_user_id)
        if like is None:
            return False
        await self.session.delete(like)
        await self.session.flush()
        return True
