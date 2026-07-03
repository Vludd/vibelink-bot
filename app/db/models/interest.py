import enum

from typing import TYPE_CHECKING    

from sqlalchemy import Enum, ForeignKey, String, Table, Column, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class InterestCategory(str, enum.Enum):
    GAMES = "games"
    IT = "it"
    MOVIES = "movies"
    MUSIC = "music"
    BOOKS = "books"
    SPORT = "sport"
    BUSINESS = "business"
    CREATIVITY = "creativity"
    SELF_GROWTH = "self_growth"


# Many-to-many: User <-> Interest
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
)


class Interest(Base):
    __tablename__ = "interests"
    __table_args__ = (UniqueConstraint("category", "name", name="uq_interest_category_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[InterestCategory] = mapped_column(Enum(InterestCategory), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    users: Mapped[list["User"]] = relationship(
        secondary=user_interests, back_populates="interests"
    )

    def __repr__(self) -> str:
        return f"<Interest {self.category}:{self.name}>"
