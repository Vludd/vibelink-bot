class GreetingService:

    def build(
        self,
        common_interests: list[str],
    ) -> str:
        if common_interests:
            return self._with_common_interest(
                common_interests[0],
            )

        return self._default()

    def _with_common_interest(
        self,
        interest: str,
    ) -> str:
        return (
            f"Привет! 👋\n\n"
            f"Увидел, что у нас совпали интересы по «{interest}».\n"
            "Решил написать и познакомиться 🙂"
        )

    def _default(self) -> str:
        return (
            "Привет! 👋\n\n"
            "Увидел, что мы стали коннектами в VibeLink.\n"
            "Решил написать и познакомиться 🙂"
        )