from sqlalchemy import delete, exists, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.block import Block


class BlockRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def block(self, blocker_id: int, blocked_id: int) -> Block:
        """Creates a block, or is a no-op if it already exists (idempotent)."""
        stmt = (
            pg_insert(Block)
            .values(blocker_id=blocker_id, blocked_id=blocked_id)
            .on_conflict_do_nothing(constraint="uq_block_blocker_blocked")
            .returning(Block)
        )
        result = await self.session.execute(stmt)
        block = result.scalar_one_or_none()
        if block is None:
            block = await self.get(blocker_id, blocked_id)
        return block

    async def unblock(self, blocker_id: int, blocked_id: int) -> bool:
        """Removes a block. Returns True if a row was actually deleted."""
        stmt = delete(Block).where(
            Block.blocker_id == blocker_id, Block.blocked_id == blocked_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get(self, blocker_id: int, blocked_id: int) -> Block | None:
        stmt = select(Block).where(
            Block.blocker_id == blocker_id, Block.blocked_id == blocked_id
        )
        return await self.session.scalar(stmt)

    async def is_blocked_either_way(self, user_a_id: int, user_b_id: int) -> bool:
        """True if either user has blocked the other — used to hide a candidate
        from search and to prevent likes/messages between the two."""
        stmt = select(
            exists().where(
                or_(
                    (Block.blocker_id == user_a_id) & (Block.blocked_id == user_b_id),
                    (Block.blocker_id == user_b_id) & (Block.blocked_id == user_a_id),
                )
            )
        )
        return bool(await self.session.scalar(stmt))

    async def get_blocked_ids(self, user_id: int) -> set[int]:
        """IDs of users that `user_id` has blocked (outgoing blocks)."""
        stmt = select(Block.blocked_id).where(Block.blocker_id == user_id)
        return set((await self.session.scalars(stmt)).all())

    async def get_blocked_by_ids(self, user_id: int) -> set[int]:
        """IDs of users who have blocked `user_id` (incoming blocks) —
        needed so a blocked user doesn't keep seeing the person who blocked them."""
        stmt = select(Block.blocker_id).where(Block.blocked_id == user_id)
        return set((await self.session.scalars(stmt)).all())

    async def get_excluded_ids(self, user_id: int) -> set[int]:
        """Union of both directions — the full set to exclude from search for this user."""
        return (await self.get_blocked_ids(user_id)) | (await self.get_blocked_by_ids(user_id))