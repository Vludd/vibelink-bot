from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    """FSM states for first profile setup."""

    choosing_goals = State()
    entering_name = State()
    entering_age = State()
    choosing_gender = State()
    choosing_search_scope = State()
    entering_city = State()
    choosing_interest_categories = State()
    choosing_interest_tags = State()
    entering_description = State()
    choosing_photo = State()
    waiting_photo = State()
    choosing_privacy = State()
    preview = State()
