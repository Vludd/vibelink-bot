from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class Like(Base):
    """A one-directional 'like' from one user to another.

    A mutual match exists when both (A -> B) and (B -> A) rows are present;
    this is detected in services/matching_service.py rather than stored
    redundantly here.
    """

    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("from_user_id", "to_user_id", name="uq_like_from_to"),
        CheckConstraint("from_user_id != to_user_id", name="ck_like_not_self"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from_user: Mapped["User"] = relationship(
        "User", foreign_keys=[from_user_id], back_populates="likes_sent"
    )
    to_user: Mapped["User"] = relationship(
        "User", foreign_keys=[to_user_id], back_populates="likes_received"
    )

    def __repr__(self) -> str:
        return f"<Like {self.from_user_id} -> {self.to_user_id}>"
