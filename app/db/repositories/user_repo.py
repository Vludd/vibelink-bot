from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.interest import Interest
from app.db.models.user import Goal, SearchScope, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int, *, with_interests: bool = False) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
        )
        
        if with_interests:
            stmt = stmt.options(selectinload(User.interests))
        
        return await self.session.scalar(stmt)

    async def get_by_telegram_id(
        self, telegram_id: int, *, with_interests: bool = False
    ) -> User | None:
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        
        if with_interests:
            stmt = stmt.options(selectinload(User.interests))
        
        return await self.session.scalar(stmt)

    async def get_or_create(
        self, 
        telegram_id: int, 
        telegram_username: str | None,
        with_interests: bool = False
    ) -> User:
        """Used on /start: returns the existing user or creates a bare row
        so onboarding (FSM) has something to attach profile data to."""
        user = await self.get_by_telegram_id(telegram_id, with_interests=with_interests)
        
        if user is not None:
            return user

        user = User(telegram_id=telegram_id, telegram_username=telegram_username)
        
        self.session.add(user)
        await self.session.flush()  # populates user.id without committing
        return user

    async def update_telegram_username(self, user: User, telegram_username: str | None) -> User:
        """Telegram usernames can change/disappear — call this on every update
        so is_searchable stays accurate."""
        user.telegram_username = telegram_username
        await self.session.flush()
        return user

    async def update_profile(self, user: User, **fields) -> User:
        """Generic profile patch used by onboarding steps, e.g.
        update_profile(user, name="Влад", age=17)."""
        for key, value in fields.items():
            if not hasattr(user, key):
                raise ValueError(f"User has no field {key!r}")
            setattr(user, key, value)
        
        await self.session.flush()
        return user

    async def set_interests(self, user: User, interests: list[Interest]) -> User:
        user.interests = interests
        await self.session.flush()
        return user

    async def mark_profile_complete(self, user: User) -> User:
        user.is_profile_complete = True
        await self.session.flush()
        return user

    async def set_hidden(self, user: User, hidden: bool) -> User:
        """Backs the 'Скрыть меня из поиска' toggle."""
        user.is_hidden = hidden
        await self.session.flush()
        return user

    async def ban(self, user: User) -> User:
        user.is_banned = True
        await self.session.flush()
        return user

    async def find_candidates(
        self,
        *,
        user_id: int,
        goal: Goal | None,
        search_scope: SearchScope | None,
        city: str | None,
        exclude_ids: set[int],
        limit: int = 20,
    ) -> list[User]:
        """Base candidate pool for matching_service to score/rank further.
        Excludes the user themselves and anything in exclude_ids (already-liked,
        blocked in either direction — passed in by the caller).
        """
        stmt = (
            select(User)
            .options(selectinload(User.interests))
            .where(
                User.id != user_id,
                # User.id.notin_(exclude_ids) if exclude_ids else True,
                User.is_profile_complete.is_(True),
                User.is_hidden.is_(False),
                User.is_banned.is_(False),
                User.telegram_username.is_not(None),
            )
        )
        
        if exclude_ids:
            stmt = stmt.where(User.id.notin_(exclude_ids))

        if goal is not None:
            stmt = stmt.where(User.goals.contains([goal]))

        if search_scope == SearchScope.CITY and city:
            stmt = stmt.where(User.city == city)

        stmt = stmt.limit(limit)
        return list((await self.session.scalars(stmt)).all())
