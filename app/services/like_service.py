from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.like import Like
from app.db.models.user import User
from app.db.repositories import LikeRepository, UserRepository


@dataclass
class LikeResult:
    like: Like
    is_match: bool
    # Populated only when is_match=True - ready to pass straight to NotificationService.
    matched_user: User | None = None
    common_interests: list[str] = field(default_factory=list)


class LikeService:
    """Sends likes and detects mutual matches.

    A 'match' is purely the presence of two Like rows in both
    directions - no separate table needed.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.like_repo = LikeRepository(session)
        self.user_repo = UserRepository(session)

    async def send_like(self, from_user_id: int, to_user_id: int) -> LikeResult:
        """Persist a like and check whether it created a mutual match."""
        like = await self.like_repo.add_like(from_user_id, to_user_id)
        is_match = await self.like_repo.is_mutual(from_user_id, to_user_id)

        matched_user: User | None = None
        common_interests: list[str] = []

        if is_match:
            matched_user = await self.user_repo.get_by_id(
                to_user_id, with_interests=True
            )
            viewer = await self.user_repo.get_by_id(
                from_user_id, with_interests=True
            )
            if viewer and matched_user:
                viewer_ids = {i.id for i in viewer.interests}
                common_interests = [
                    i.name
                    for i in matched_user.interests
                    if i.id in viewer_ids
                ]

        return LikeResult(
            like=like,
            is_match=is_match,
            matched_user=matched_user,
            common_interests=common_interests,
        )

    async def get_match_ids(self, user_id: int) -> set[int]:
        """Powers 'My matches' list."""
        return await self.like_repo.get_match_ids(user_id)

    async def get_received_ids(self, user_id: int) -> set[int]:
        """Powers 'Who liked me' list."""
        return await self.like_repo.get_received_ids(user_id)

    async def remove_like(self, from_user_id: int, to_user_id: int) -> bool:
        """'Remove like' - optional feature for future iterations."""
        return await self.like_repo.remove_like(from_user_id, to_user_id)
    
    async def create_match(
        self,
        user_a_id: int,
        user_b_id: int,
    ) -> LikeResult:
        """Create a mutual match between two users."""

        await self.send_like(
            from_user_id=user_a_id,
            to_user_id=user_b_id,
        )

        return await self.send_like(
            from_user_id=user_b_id,
            to_user_id=user_a_id,
        )
    
    async def get_matches(
        self,
        user_id: int,
        *,
        with_interests: bool = False,
    ) -> list[User]:
        return await self.like_repo.get_matches(user_id, with_interests=with_interests)
    
    async def get_match(
        self,
        user_id: int,
        connected_user_id: int,
        *,
        with_interests: bool = False,
    ) -> User | None:
        matches = await self.get_matches(
            user_id,
            with_interests=with_interests,
        )

        return next(
            (
                user
                for user in matches
                if user.id == connected_user_id
            ),
            None,
        )
