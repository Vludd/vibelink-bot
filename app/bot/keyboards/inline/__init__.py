from app.bot.keyboards.inline.onboarding import (
    kb_goals,
    kb_gender,
    kb_search_scope,
    kb_interest_categories,
    kb_interest_tags,
    kb_communication_format,
    kb_privacy,
    kb_preview_confirm,
)
from app.bot.keyboards.inline.search import (
    kb_search_goal,
    kb_candidate_card,
    kb_search_filters,
)
from app.bot.keyboards.inline.match import (
    kb_match_actions,
    kb_copy_greeting,
)
from app.bot.keyboards.inline.profile import (
    kb_main_menu,
    kb_profile_menu,
    kb_profile_edit,
    kb_hidden_toggle,
    kb_report_reason,
)

__all__ = [
    # onboarding
    "kb_goals",
    "kb_gender",
    "kb_search_scope",
    "kb_interest_categories",
    "kb_interest_tags",
    "kb_communication_format",
    "kb_privacy",
    "kb_preview_confirm",
    # search
    "kb_search_goal",
    "kb_candidate_card",
    "kb_search_filters",
    # match
    "kb_match_actions",
    "kb_copy_greeting",
    # profile / moderation
    "kb_main_menu",
    "kb_profile_menu",
    "kb_profile_edit",
    "kb_hidden_toggle",
    "kb_report_reason",
]