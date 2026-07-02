"""Клавиатуры для шагов онбординга.

Соглашения по callback_data:
  ob:<action>:<value>

Примеры:
  ob:goal:teammate
  ob:gender:male
  ob:scope:online
  ob:cat:games          ← выбор категории интересов
  ob:tag:42             ← выбор конкретного тега (id из БД)
  ob:fmt:voice          ← формат общения
  ob:priv:show_age:1    ← переключение приватности
  ob:done               ← «Готово» внутри шага с мультивыбором
  ob:confirm            ← подтвердить анкету на превью
  ob:edit               ← редактировать анкету на превью
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.user import Goal, Gender, SearchScope
from app.db.models.interest import Interest, InterestCategory


# ─────────────────────────────── helpers ──────────────────────────────────

_PREFIX = "ob"

GOAL_LABELS: dict[Goal, str] = {
    Goal.FRIEND:       "👥 Друга",
    Goal.RELATIONSHIP: "💜 Девушку / парня",
    Goal.TEAMMATE:     "🎮 Тиммейта для игр",
    Goal.BUSINESS:     "💼 Для бизнеса",
    Goal.PROJECT:      "🧑‍💻 Для проекта",
    Goal.TALK:         "💬 Просто пообщаться",
}

GENDER_LABELS: dict[Gender, str] = {
    Gender.MALE:   "👦 Парень",
    Gender.FEMALE: "👧 Девушка",
    Gender.OTHER:  "🌈 Другое",
}

SCOPE_LABELS: dict[SearchScope, str] = {
    SearchScope.CITY:   "📍 В моём городе",
    SearchScope.ONLINE: "🌍 Онлайн",
    SearchScope.CIS:    "🇷🇺 По России / СНГ",
}

CATEGORY_LABELS: dict[InterestCategory, str] = {
    InterestCategory.GAMES:       "🎮 Игры",
    InterestCategory.IT:          "💻 IT",
    InterestCategory.MOVIES:      "🎬 Кино",
    InterestCategory.MUSIC:       "🎵 Музыка",
    InterestCategory.BOOKS:       "📚 Книги",
    InterestCategory.SPORT:       "🏋️ Спорт",
    InterestCategory.BUSINESS:    "💼 Бизнес",
    InterestCategory.CREATIVITY:  "🎨 Творчество",
    InterestCategory.SELF_GROWTH: "🧠 Саморазвитие",
}

FORMAT_OPTIONS: list[tuple[str, str]] = [
    ("💬 Переписка",         "chat"),
    ("🎧 Голос",             "voice"),
    ("🎮 Играть вместе",     "play"),
    ("☕ Встретиться офлайн","offline"),
    ("🧑‍💻 Делать проект",    "project"),
]


def _btn(text: str, *data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=f"{_PREFIX}:" + ":".join(data))


def _done_btn(step: str) -> InlineKeyboardButton:
    return _btn("✅ Готово", "done", step)


# ──────────────────────────── публичные фабрики ───────────────────────────


def kb_onboarding_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("🚀 Заполнить профиль", "start")],
            [_btn("ℹ️ Как это работает", "how")],
            # добавить кнопку назад?
        ]
    )


def kb_username_required() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("✅ Проверить username", "username", "check")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")],
        ]
    )


def kb_goals(selected: set[Goal] | None = None) -> InlineKeyboardMarkup:
    """Мультивыбор целей. Выбранные — с галочкой."""
    selected = selected or set()
    builder = InlineKeyboardBuilder()
    for goal, label in GOAL_LABELS.items():
        mark = "✅ " if goal in selected else ""
        builder.button(
            text=f"{mark}{label}",
            callback_data=f"{_PREFIX}:goal:{goal.value}",
        )
    builder.adjust(1)
    if selected:
        builder.row(_done_btn("goals"))
    return builder.as_markup()


def kb_gender() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for gender, label in GENDER_LABELS.items():
        builder.button(text=label, callback_data=f"{_PREFIX}:gender:{gender.value}")
    builder.adjust(1)
    return builder.as_markup()


def kb_search_scope() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for scope, label in SCOPE_LABELS.items():
        builder.button(text=label, callback_data=f"{_PREFIX}:scope:{scope.value}")
    builder.adjust(1)
    return builder.as_markup()


def kb_interest_categories(selected_cats: set[InterestCategory] | None = None) -> InlineKeyboardMarkup:
    """Первый уровень выбора интересов — категории."""
    selected_cats = selected_cats or set()
    builder = InlineKeyboardBuilder()
    for cat, label in CATEGORY_LABELS.items():
        mark = "✅ " if cat in selected_cats else ""
        builder.button(
            text=f"{mark}{label}",
            callback_data=f"{_PREFIX}:cat:{cat.value}",
        )
    builder.adjust(2)
    if selected_cats:
        builder.row(_done_btn("interests"))
    return builder.as_markup()


def kb_interest_tags(
    interests: list[Interest],
    selected_ids: set[int] | None = None,
    category: InterestCategory | None = None,
) -> InlineKeyboardMarkup:
    """Теги внутри категории. selected_ids — уже выбранные пользователем."""
    selected_ids = selected_ids or set()
    builder = InlineKeyboardBuilder()
    for interest in interests:
        mark = "✅ " if interest.id in selected_ids else ""
        builder.button(
            text=f"{mark}{interest.name}",
            callback_data=f"{_PREFIX}:tag:{interest.id}",
        )
    builder.adjust(2)
    # Назад к категориям
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"{_PREFIX}:back:cats"))
    if selected_ids:
        builder.row(_done_btn(f"tags:{category.value if category else ''}"))
    return builder.as_markup()


def kb_communication_format(selected: set[str] | None = None) -> InlineKeyboardMarkup:
    """Мультивыбор формата общения."""
    selected = selected or set()
    builder = InlineKeyboardBuilder()
    for label, value in FORMAT_OPTIONS:
        mark = "✅ " if value in selected else ""
        builder.button(text=f"{mark}{label}", callback_data=f"{_PREFIX}:fmt:{value}")
    builder.adjust(1)
    if selected:
        builder.row(_done_btn("format"))
    return builder.as_markup()


def kb_photo_choice() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn("📸 Добавить фото", "photo", "add")],
            [_btn("Пропустить", "photo", "skip")],
        ]
    )


def kb_privacy(show_age: bool = True, show_city: bool = True) -> InlineKeyboardMarkup:
    """Переключатели приватности — тоггл, ✅/⬜."""
    def _toggle(flag: bool, field: str, label: str) -> InlineKeyboardButton:
        icon = "✅" if flag else "⬜"
        new_val = "0" if flag else "1"
        return InlineKeyboardButton(
            text=f"{icon} {label}",
            callback_data=f"{_PREFIX}:priv:{field}:{new_val}",
        )

    return InlineKeyboardMarkup(inline_keyboard=[
        [_toggle(show_age,  "show_age",  "Показывать возраст")],
        [_toggle(show_city, "show_city", "Показывать город")],
        [_btn("✅ Готово", "done", "privacy")],
    ])


def kb_preview_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("✅ Всё ок — начать поиск", "confirm")],
        [_btn("✏️ Изменить", "edit")],
    ])