from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import Goal, User
from app.db.repositories import BlockRepository, LikeRepository, UserRepository


@dataclass
class CandidateCard:
    """A scored, display-ready candidate returned to the handler."""

    user: User
    # Jaccard similarity over interest sets, expressed as 0–100.
    score: int
    common_interests: list[str] = field(default_factory=list)


def _jaccard_score(set_a: set[int], set_b: set[int]) -> int:
    """Jaccard index as an integer percentage (0–100)."""
    union = set_a | set_b
    if not union:
        return 0
    return int(len(set_a & set_b) / len(union) * 100)


class MatchingService:
    """Builds a ranked list of candidates for a given viewer.

    Strategy
    --------
    1. Build exclude_ids = already-liked ∪ blocks (both directions).
    2. Fetch a raw pool from user_repo.find_candidates() (applies goal +
       scope/city filters at the DB level).
    3. Score each candidate by Jaccard interest overlap with the viewer.
    4. Return top-N sorted by score descending.

    The over-fetch factor (× POOL_MULTIPLIER) compensates for the fact that
    DB-level filtering can't apply the interest score — we fetch more rows
    than we need so that post-scoring still yields `limit` good results.
    """

    POOL_MULTIPLIER = 4

    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.like_repo = LikeRepository(session)
        self.block_repo = BlockRepository(session)

    async def get_candidates(
        self,
        viewer: User,
        *,
        goal: Goal | None = None,
        limit: int = 10,
    ) -> list[CandidateCard]:
        """Return up to `limit` scored candidate cards for the viewer."""
        liked_ids = await self.like_repo.get_sent_ids(viewer.id)
        blocked_ids = await self.block_repo.get_excluded_ids(viewer.id)
        exclude_ids = liked_ids | blocked_ids | {viewer.id}

        raw_pool = await self.user_repo.find_candidates(
            user_id=viewer.id,
            goal=goal,
            search_scope=viewer.search_scope,
            city=viewer.city,
            exclude_ids=exclude_ids,
            limit=limit * self.POOL_MULTIPLIER,
        )

        viewer_interest_ids = {i.id for i in (viewer.interests or [])}

        cards: list[CandidateCard] = []
        for candidate in raw_pool:
            candidate_interest_ids = {i.id for i in (candidate.interests or [])}
            score = _jaccard_score(viewer_interest_ids, candidate_interest_ids)
            common = [
                i.name
                for i in (candidate.interests or [])
                if i.id in viewer_interest_ids
            ]
            cards.append(
                CandidateCard(user=candidate, score=score, common_interests=common)
            )

        cards.sort(key=lambda c: c.score, reverse=True)
        return cards[:limit]
