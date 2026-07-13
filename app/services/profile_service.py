from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.interest import Interest
from app.db.models.user import Gender, Goal, SearchScope, User
from app.db.repositories import InterestRepository, UserRepository
from app.services.dto.profile import ProfileData


class ProfileService:
    """Handles all profile lifecycle: creation, onboarding steps, visibility."""

    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.interest_repo = InterestRepository(session)

    async def get_or_create(
        self, telegram_id: int, telegram_username: str | None
    ) -> User:
        """/start entry-point: returns existing user or creates a bare row."""
        return await self.user_repo.get_or_create(telegram_id, telegram_username)

    async def sync_username(self, user: User, telegram_username: str | None) -> User:
        """Call on every incoming update so is_searchable stays accurate."""
        if user.telegram_username != telegram_username:
            return await self.user_repo.update_telegram_username(user, telegram_username)
        return user

    async def update(self, user: User, **fields) -> User:
        """Patch any profile scalar fields (name, age, city, description, …)."""
        return await self.user_repo.update_profile(user, **fields)

    async def set_goals(self, user: User, goals: list[Goal]) -> User:
        return await self.user_repo.update_profile(user, goals=goals)

    async def set_gender(self, user: User, gender: Gender) -> User:
        return await self.user_repo.update_profile(user, gender=gender)

    async def set_search_scope(
        self, user: User, scope: SearchScope, city: str | None = None
    ) -> User:
        fields: dict = {"search_scope": scope}
        if scope == SearchScope.CITY:
            fields["city"] = city
        return await self.user_repo.update_profile(user, **fields)

    async def set_interests_by_ids(
        self, user: User, interest_ids: list[int]
    ) -> User:
        """Resolve button IDs → Interest rows → replace user's interest list."""
        interests = await self.interest_repo.get_by_ids(interest_ids)
        return await self.user_repo.set_interests(user, interests)

    async def set_privacy(
        self, user: User, *, show_age: bool, show_city: bool
    ) -> User:
        return await self.user_repo.update_profile(
            user, show_age=show_age, show_city=show_city
        )

    async def complete_profile(self, user: User) -> User:
        """Mark onboarding done — makes the profile appear in search."""
        return await self.user_repo.mark_profile_complete(user)

    async def set_hidden(self, user: User, hidden: bool) -> User:
        """'Скрыть меня из поиска' toggle."""
        return await self.user_repo.set_hidden(user, hidden)

    async def get_by_telegram_id(
        self, telegram_id: int, *, with_interests: bool = False
    ) -> User | None:
        return await self.user_repo.get_by_telegram_id(
            telegram_id, with_interests=with_interests
        )
    
    async def toggle_hidden(self, user: User) -> User:
        return await self.user_repo.set_hidden(
            user,
            not user.is_hidden,
        )
        
    async def bootstrap_profile(
        self,
        user: User,
        profile: ProfileData,
    ) -> User:
        """Fill a profile in a single operation.

        Used by development tools and automated tests.
        """

        await self.user_repo.update_profile(
            user,
            name=profile.name,
            age=profile.age,
            gender=profile.gender,
            city=profile.city,
            search_scope=profile.search_scope,
            goals=profile.goals,
            description=profile.description,
            photo_file_id=profile.photo_file_id,
            show_age=profile.show_age,
            show_city=profile.show_city,
        )

        await self.user_repo.set_interests(
            user,
            profile.interests,
        )

        await self.user_repo.mark_profile_complete(
            user,
        )

        return user
