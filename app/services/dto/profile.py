from __future__ import annotations

import random
from dataclasses import dataclass

from faker import Faker

from app.db.models.interest import Interest
from app.db.models.user import (
    Gender,
    Goal,
    SearchScope,
)

fake = Faker("ru_RU")


@dataclass(slots=True)
class ProfileData:
    """Full profile data used for bootstrapping a completed profile.

    Intended for development utilities, automated tests and data import.
    """

    name: str
    age: int
    gender: Gender

    city: str
    search_scope: SearchScope

    goals: list[Goal]
    interests: list[Interest]

    description: str
    photo_file_id: str | None = None

    show_age: bool = True
    show_city: bool = True

    @classmethod
    def random(
        cls,
        *,
        interests: list[Interest],
        cities: list[str],
    ) -> "ProfileData":
        """Generate a realistic random profile."""

        if len(interests) < 3:
            raise ValueError(
                "At least 3 interests are required to generate a profile."
            )

        return cls(
            name=fake.first_name(),
            age=random.randint(18, 45),
            gender=random.choice(list(Gender)),
            city=random.choice(cities),
            search_scope=random.choice(list(SearchScope)),
            goals=random.sample(
                list(Goal),
                k=random.randint(1, 3),
            ),
            interests=random.sample(
                interests,
                k=random.randint(
                    3,
                    min(8, len(interests)),
                ),
            ),
            description=fake.text(max_nb_chars=180),
            show_age=random.choice([True, False]),
            show_city=random.choice([True, False]),
        )