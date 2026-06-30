import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, Enum, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.models.interest import Interest, user_interests

if TYPE_CHECKING:
    from app.db.models.like import Like
    from app.db.models.block import Block
    from app.db.models.report import Report


class Goal(str, enum.Enum):
    FRIEND = "friend"
    RELATIONSHIP = "relationship"
    TEAMMATE = "teammate"
    BUSINESS = "business"
    PROJECT = "project"
    TALK = "talk"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class SearchScope(str, enum.Enum):
    CITY = "city"
    ONLINE = "online"
    CIS = "cis"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Profile
    name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    search_scope: Mapped[Optional[SearchScope]] = mapped_column(Enum(SearchScope), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Multi-select goals, e.g. ["teammate", "project"]
    goals: Mapped[Optional[list[Goal]]] = mapped_column(
        ARRAY(Enum(Goal, name="goal_enum")), nullable=True
    )

    # Privacy toggles — what is shown to other users before a mutual match
    show_age: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_city: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Onboarding / moderation state
    is_profile_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    interests: Mapped[list[Interest]] = relationship(
        secondary=user_interests, back_populates="users"
    )

    likes_sent: Mapped[list["Like"]] = relationship(
        "Like", foreign_keys="Like.from_user_id", back_populates="from_user"
    )
    likes_received: Mapped[list["Like"]] = relationship(
        "Like", foreign_keys="Like.to_user_id", back_populates="to_user"
    )
    blocks_made: Mapped[list["Block"]] = relationship(
        "Block", foreign_keys="Block.blocker_id", back_populates="blocker"
    )
    reports_made: Mapped[list["Report"]] = relationship(
        "Report", foreign_keys="Report.reporter_id", back_populates="reporter"
    )

    @property
    def is_searchable(self) -> bool:
        """User must have a public username and a complete, non-hidden, non-banned profile."""
        return bool(
            self.telegram_username
            and self.is_profile_complete
            and not self.is_hidden
            and not self.is_banned
        )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg_id={self.telegram_id} name={self.name!r}>"