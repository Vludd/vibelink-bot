from html import escape
import logging

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from app.db.models.user import User

logger = logging.getLogger(__name__)

_MATCH_TEXT = """\
🎉 <b>У тебя новый коннект!</b>

<b>{other_name}</b> тоже хочет пообщаться с тобой.

<b>Общие интересы:</b>
{interests}

💬 Можешь написать:
@{username}

<i>Удачи! 🤝</i>
"""

_GREETING_HINT = (
    "Привет! Увидел(а), что у нас совпали интересы по {top_interest}. "
    "Может, пообщаемся? 🙂"
)


def _format_interests(names: list[str]) -> str:
    if not names:
        return "• нет общих интересов"

    return "\n".join(
        f"• {escape(name)}"
        for name in names[:5]
    )


class NotificationService:
    """Sends Telegram messages on behalf of the bot.

    Intentionally thin - no DB access here, just message delivery.
    All data must be pre-fetched by the caller (LikeService / handlers).
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def build_greeting_hint(self, common_interests: list[str]) -> str:
        """Ready-to-copy first message for the user to send their new connect."""
        top = common_interests[0] if common_interests else "общим интересам"
        return _GREETING_HINT.format(top_interest=top)

    async def notify_match(
        self,
        user: User,
        matched_with: User,
        common_interests: list[str],
    ) -> bool:
        """Send a match notification to `user` about `matched_with`.

        Returns True if the message was delivered, False if the user blocked
        the bot (TelegramForbiddenError) or another delivery error occurred.
        """
        if not matched_with.telegram_username:
            # Should not happen - is_searchable guards against this,
            # but guard here too to avoid a broken notification.
            logger.warning(
                "notify_match: matched_with (id=%s) has no username, skipping",
                matched_with.id,
            )
            return False

        text = _MATCH_TEXT.format(
            other_name = escape(matched_with.name or "Пользователь"),
            interests=_format_interests(common_interests),
            username = escape(matched_with.telegram_username)
        )

        try:
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=text,
            )
            return True
        except TelegramForbiddenError:
            logger.info(
                "notify_match: bot is blocked by tg_id=%s",
                user.telegram_id,
            )
            return False

        except TelegramBadRequest as e:
            logger.debug(
                "notify_match: tg_id=%s skipped: %s",
                user.telegram_id,
                e.message,
            )
            return False

        except TelegramRetryAfter as e:
            logger.warning(
                "notify_match: retry after %ss",
                e.retry_after,
            )
            return False

        except Exception:
            logger.exception(
                "notify_match: unexpected error for tg_id=%s",
                user.telegram_id,
            )
            return False

    async def notify_both_on_match(
        self,
        user_a: User,
        user_b: User,
        common_interests: list[str],
    ) -> None:
        """Notify both sides of a mutual match. Called by LikeService handler."""
        await self.notify_match(user_a, matched_with=user_b, common_interests=common_interests)
        await self.notify_match(user_b, matched_with=user_a, common_interests=common_interests)
