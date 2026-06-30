from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class Block(Base):
    """blocker hides blocked from their search results and incoming likes."""

    __tablename__ = "blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_block_blocker_blocked"),
        CheckConstraint("blocker_id != blocked_id", name="ck_block_not_self"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    blocker_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    blocked_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    blocker: Mapped["User"] = relationship(
        "User", foreign_keys=[blocker_id], back_populates="blocks_made"
    )
    blocked: Mapped["User"] = relationship("User", foreign_keys=[blocked_id])

    def __repr__(self) -> str:
        return f"<Block {self.blocker_id} blocked {self.blocked_id}>"