from aiogram.fsm.state import State, StatesGroup


class SearchState(StatesGroup):
    """FSM states for search functionality."""

    searching = State()