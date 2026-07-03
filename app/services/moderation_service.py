import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.block import Block
from app.db.models.report import Report, ReportReason, ReportStatus
from app.db.models.user import User
from app.db.repositories import BlockRepository, ReportRepository, UserRepository

logger = logging.getLogger(__name__)

# Auto-hide a profile once this many pending reports accumulate.
# Keeps flagged content off search while a human reviews it.
AUTO_HIDE_THRESHOLD = 3


class ModerationService:
    """Handles blocks, reports, and admin moderation actions (ban/dismiss)."""

    def __init__(self, session: AsyncSession) -> None:
        self.block_repo = BlockRepository(session)
        self.report_repo = ReportRepository(session)
        self.user_repo = UserRepository(session)

    # ------------------------------------------------------------------ blocks

    async def block_user(self, blocker_id: int, blocked_id: int) -> Block:
        """Block another user (idempotent)."""
        return await self.block_repo.block(blocker_id, blocked_id)

    async def unblock_user(self, blocker_id: int, blocked_id: int) -> bool:
        """Remove a block. Returns True if a row was actually deleted."""
        return await self.block_repo.unblock(blocker_id, blocked_id)

    async def is_blocked_either_way(self, user_a_id: int, user_b_id: int) -> bool:
        return await self.block_repo.is_blocked_either_way(user_a_id, user_b_id)

    # ----------------------------------------------------------------- reports

    async def report_user(
        self,
        reporter_id: int,
        reported_id: int,
        reason: ReportReason,
        comment: str | None = None,
    ) -> Report:
        """File a report and auto-hide the reported profile if the threshold
        of pending reports is reached."""
        report = await self.report_repo.create(
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            comment=comment,
        )

        pending = await self.report_repo.count_pending_for_user(reported_id)
        if pending >= AUTO_HIDE_THRESHOLD:
            reported_user = await self.user_repo.get_by_id(reported_id)
            if reported_user and not reported_user.is_hidden:
                await self.user_repo.set_hidden(reported_user, True)
                logger.info(
                    "moderation: auto-hidden user id=%s after %s pending reports",
                    reported_id,
                    pending,
                )

        return report

    # --------------------------------------------------- admin moderation actions

    async def ban_user(self, user: User) -> User:
        """Ban a user and bulk-resolve all their pending reports as REVIEWED."""
        user = await self.user_repo.ban(user)
        resolved = await self.report_repo.resolve_all_for_user(
            user.id, ReportStatus.REVIEWED
        )
        logger.info(
            "moderation: banned user id=%s, resolved %s report(s)", user.id, resolved
        )
        return user

    async def dismiss_reports(self, reported_id: int) -> int:
        """Admin dismisses reports against a user (profile was reviewed, no violation).
        Also un-hides the profile if it was auto-hidden.
        Returns the number of reports closed."""
        reported_user = await self.user_repo.get_by_id(reported_id)
        if reported_user and reported_user.is_hidden and not reported_user.is_banned:
            await self.user_repo.set_hidden(reported_user, False)

        resolved = await self.report_repo.resolve_all_for_user(
            reported_id, ReportStatus.DISMISSED
        )
        logger.info(
            "moderation: dismissed %s report(s) for user id=%s", resolved, reported_id
        )
        return resolved

    async def get_pending_reports(
        self, *, limit: int = 50, offset: int = 0
    ) -> list[Report]:
        """Moderation queue for an admin panel / handler."""
        return await self.report_repo.list_pending(limit=limit, offset=offset)
