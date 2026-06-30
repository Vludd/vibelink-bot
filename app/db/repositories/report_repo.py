from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.report import Report, ReportReason, ReportStatus


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        reporter_id: int,
        reported_id: int,
        reason: ReportReason,
        comment: str | None = None,
    ) -> Report:
        """Not idempotent on purpose — the same pair can file multiple reports
        over time (e.g. repeated harassment), unlike Like/Block which are
        one-shot relationships."""
        report = Report(
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            comment=comment,
        )
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_by_id(self, report_id: int) -> Report | None:
        return await self.session.get(Report, report_id)

    async def list_pending(self, *, limit: int = 50, offset: int = 0) -> list[Report]:
        """Moderation queue, oldest first (FIFO)."""
        stmt = (
            select(Report)
            .options(selectinload(Report.reporter), selectinload(Report.reported))
            .where(Report.status == ReportStatus.PENDING)
            .order_by(Report.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_for_user(
        self, reported_id: int, *, limit: int = 50
    ) -> list[Report]:
        """All reports filed against a given user — for an admin looking up
        a specific profile's history before banning."""
        stmt = (
            select(Report)
            .where(Report.reported_id == reported_id)
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.scalars(stmt)).all())

    async def count_pending_for_user(self, reported_id: int) -> int:
        """Useful as an auto-flag trigger, e.g. 'hide profile after N pending reports'."""
        stmt = select(func.count()).select_from(Report).where(
            Report.reported_id == reported_id, Report.status == ReportStatus.PENDING
        )
        return int(await self.session.scalar(stmt) or 0)

    async def set_status(self, report: Report, status: ReportStatus) -> Report:
        report.status = status
        await self.session.flush()
        return report

    async def resolve_all_for_user(
        self, reported_id: int, status: ReportStatus = ReportStatus.REVIEWED
    ) -> int:
        """Bulk-close pending reports once a moderation action (e.g. ban) is taken.
        Returns the number of rows updated."""
        stmt = (
            select(Report)
            .where(Report.reported_id == reported_id, Report.status == ReportStatus.PENDING)
        )
        reports = list((await self.session.scalars(stmt)).all())
        for report in reports:
            report.status = status
        await self.session.flush()
        return len(reports)