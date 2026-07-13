from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Any


def h(value: Any) -> str:
    """
    Escape user-generated content for Telegram HTML parse mode.

    Important:
    Bot uses ParseMode.HTML, so every user text must be escaped before rendering.
    """
    if value is None:
        return ""
    return escape(str(value), quote=False)


def join_items(items: Sequence[Any] | None, default: str = "—") -> str:
    if not items:
        return default

    prepared = [h(item).strip() for item in items if str(item).strip()]
    return ", ".join(prepared) if prepared else default


def value_or_dash(value: Any) -> str:
    if value is None:
        return "—"

    text = h(value).strip()
    return text if text else "—"


def username_link(username: str | None) -> str:
    if not username:
        return "username не задан"

    username = username.strip().lstrip("@")
    if not username:
        return "username не задан"

    return f"@{h(username)}"


# =========================
# Common
# =========================

BOT_NAME = "VibeLink"

UNKNOWN_COMMAND = (
    "Не понял команду.\n\n"
    "Используй /start, чтобы открыть главное меню."
)

PING_TEXT = "pong ✅"

ACTION_IN_DEV = "Пока это dev-заглушка ✅"

BACK_TO_MENU = "Вернуться в меню"

CANCELLED = "Действие отменено."

SOMETHING_WENT_WRONG = (
    "Что-то пошло не так.\n\n"
    "Попробуй еще раз чуть позже."
)


# =========================
# Start / Main menu
# =========================

def start_text(telegram_username: str | None = None) -> str:
    username = username_link(telegram_username)

    return (
        f"👋 <b>{BOT_NAME}</b>\n\n"
        "Я помогу найти людей на одной волне: для общения, игр, проектов, "
        "бизнеса или знакомств.\n\n"
        "Сначала заполним короткий профиль, потом ты сможешь смотреть карточки "
        "людей с похожими интересами.\n\n"
        f"Твой Telegram username: <b>{username}</b>"
    )


HOW_IT_WORKS = (
    "ℹ️ <b>Как это работает</b>\n\n"
    "1. Ты заполняешь короткий профиль.\n"
    "2. Выбираешь цели и интересы.\n"
    "3. Я показываю людей, которые подходят тебе по совпадениям.\n"
    "4. Если вы оба нажали «Нравится», появляется коннект.\n"
    "5. После коннекта открывается Telegram username собеседника.\n\n"
    "Контакт не показывается заранее, чтобы не было спама и неприятных сообщений."
)

MAIN_MENU = (
    "🏠 <b>Главное меню</b>\n\n"
    "Что хочешь сделать?"
)

PROFILE_REQUIRED = (
    "Сначала нужно заполнить профиль.\n\n"
    "Без профиля я не смогу нормально подобрать людей по интересам."
)


# =========================
# Username
# =========================

USERNAME_REQUIRED = (
    "⚠️ <b>У тебя не установлен Telegram username</b>\n\n"
    "Username обязателен: после взаимного коннекта "
    "бот сможет дать собеседнику ссылку на твой профиль.\n\n"
    "Установить username можно в Telegram:\n"
    "<b>Настройки → Имя пользователя</b>"
)

USERNAME_OK = (
    "✅ Username найден.\n\n"
    "После взаимного коннекта собеседник сможет перейти к тебе в ЛС."
)


# =========================
# Onboarding
# =========================

ONBOARDING_START = (
    "Отлично. Давай соберем профиль, чтобы я мог подобрать людей точнее."
)

ONBOARDING_RESTART = (
    "Ок, заполним анкету заново. Старые данные перезапишутся после каждого шага."
)

ASK_GOALS = (
    "🎯 <b>Кого ты хочешь найти?</b>\n\n"
    "Можно выбрать несколько вариантов."
)

ASK_NAME = (
    "Как тебя показывать другим?\n\n"
    "Введи настоящее имя. Например: Анфиса, Артем"
)

ASK_AGE = (
    "Сколько тебе лет?\n\n"
    "Напиши возраст числом."
)

ASK_GENDER = (
    "Укажи пол.\n\n"
    "Это поможет аккуратнее показывать анкету и позже настроить фильтры."
)

ASK_LOCATION_MODE = (
    "Где искать людей?"
)

ASK_CITY = (
    "Напиши город.\n\n"
    "Например: Алматы"
)

ASK_INTEREST_CATEGORIES = (
    "🏷 <b>Выбери категории интересов</b>\n\n"
    "Чем точнее интересы, тем лучше будут рекомендации."
)

ASK_INTERESTS = (
    "Теперь выбери конкретные интересы."
)

ASK_COMMUNICATION_FORMAT = (
    "Какой формат общения тебе ближе?"
)

ASK_DESCRIPTION = (
    "📝 <b>Расскажи коротко о себе</b>\n\n"
    "Лучше 2–3 предложения.\n\n"
    "Можно по шаблону:\n"
    "<i>Увлекаюсь ..., ищу ..., обычно свободен ...</i>"
)

ASK_PHOTO = (
    "📸 Хочешь добавить фото?\n\n"
    "Профили с фото обычно получают больше откликов.\n"
    "Для игр, проектов и бизнеса можно использовать обычную аватарку."
)

ASK_PHOTO_UPLOAD = (
    "Отправь фото одним сообщением.\n\n"
    "Если передумал — нажми «Пропустить»."
)

ASK_PRIVACY = (
    "🔐 <b>Приватность</b>\n\n"
    "Что показывать другим пользователям в карточке?"
)

PROFILE_SAVED = (
    "✅ Профиль сохранен.\n\n"
    "Теперь можно начинать поиск людей."
)

PROFILE_SKIPPED_PHOTO = (
    "Ок, фото можно добавить позже."
)


# =========================
# Validation
# =========================

INVALID_NAME = (
    "Имя выглядит странно.\n\n"
    "Напиши коротко, как тебя показывать другим. Например: Анфиса, Артем"
)

INVALID_AGE = (
    "Возраст нужно указать числом.\n\n"
    "Например: 21"
)

AGE_TOO_LOW = (
    "Пока нельзя продолжить с таким возрастом."
)

AGE_TOO_HIGH = (
    "Возраст выглядит нереалистично.\n\n"
    "Проверь число и отправь еще раз."
)

INVALID_DESCRIPTION = (
    "Описание слишком короткое.\n\n"
    "Напиши хотя бы пару слов о себе и о том, кого хочешь найти."
)

INVALID_CITY = (
    "Город выглядит странно.\n\n"
    "Напиши коротко: Алматы, Астана, Москва и т.д."
)

INVALID_PHOTO = (
    "Нужно отправить именно фото.\n\n"
    "Не файл, не стикер, не текст — обычную фотографию."
)

NEED_SELECT_GOAL = "Выбери хотя бы одну цель."
NEED_SELECT_INTEREST = "Выбери хотя бы один интерес."


# =========================
# Profile
# =========================

def profile_preview(profile: Mapping[str, Any]) -> str:
    name = value_or_dash(profile.get("name"))
    age = value_or_dash(profile.get("age"))
    city = value_or_dash(profile.get("city"))
    search_scope = value_or_dash(profile.get("search_scope"))
    gender = value_or_dash(profile.get("gender"))

    goals = join_items(profile.get("goals"))
    interests = join_items(profile.get("interests"))
    description = value_or_dash(profile.get("description"))

    return (
        f"👤 <b>{name}, {age}</b>\n"
        f"📍 <b>Город:</b> {city}\n"
        f"🌍 <b>Формат поиска:</b> {search_scope}\n"
        f"🚻 <b>Пол:</b> {gender}\n\n"
        f"🎯 <b>Цели:</b>\n"
        f"{goals}\n\n"
        f"🏷 <b>Интересы:</b>\n"
        f"{interests}\n\n"
        f"📝 <b>О себе:</b>\n"
        f"{description}"
    )


def profile_view(profile: Mapping[str, Any]) -> str:
    return (
        "👤 <b>Мой профиль</b>\n\n"
        f"{profile_preview(profile)}"
    )


PROFILE_EDIT_MENU = (
    "✏️ <b>Редактирование профиля</b>\n\n"
    "Что хочешь изменить?"
)

PROFILE_HIDDEN = (
    "⏸ Профиль скрыт из поиска.\n\n"
    "Другие пользователи не будут видеть тебя в рекомендациях."
)

PROFILE_VISIBLE = (
    "▶️ Профиль снова виден в поиске."
)


# =========================
# Search
# =========================

SEARCH_MODE_SELECT = (
    "🔎 <b>Кого ищем сейчас?</b>\n\n"
    "Выбери режим поиска."
)

SEARCH_STARTED = (
    "Ищу людей с похожими интересами..."
)

NO_CANDIDATES = (
    "Пока нет подходящих людей.\n\n"
    "Можно попробовать изменить фильтры или зайти позже."
)

NO_MORE_CANDIDATES = (
    "На сейчас карточки закончились.\n\n"
    "Позже могут появиться новые люди."
)

INVALID_SEARCH_MODE = "Неизвестный режим поиска."
USER_IS_NOT_FOUND = "Пользователь не найден."


def candidate_card(candidate: Mapping[str, Any]) -> str:
    name = value_or_dash(candidate.get("name"))
    age = value_or_dash(candidate.get("age"))
    city = candidate.get("city")
    is_online = bool(candidate.get("is_online", True))

    location = "Онлайн"
    if city and is_online:
        location = f"{h(city)} / Онлайн"
    elif city:
        location = h(city)

    match_percent = candidate.get("match_percent")
    match_text = f"{h(match_percent)}%" if match_percent is not None else "—"

    common_interests = join_items(candidate.get("common_interests"))
    goals = join_items(candidate.get("goals"))
    looking_for = value_or_dash(candidate.get("looking_for"))
    description = value_or_dash(candidate.get("description"))

    return (
        "🔎 <b>Нашел человека с похожими интересами</b>\n\n"
        f"👤 <b>{name}, {age}</b>\n"
        f"📍 {location}\n\n"
        f"📊 <b>Совпадение:</b> {match_text}\n\n"
        f"🤝 <b>Общие интересы:</b>\n"
        f"{common_interests}\n\n"
        f"🎯 <b>Цели:</b>\n"
        f"{goals}\n\n"
        f"📝 <b>О себе:</b>\n"
        f"{description}\n\n"
        f"🔎 <b>Ищет:</b>\n"
        f"{looking_for}"
    )


def like_sent(candidate_name: str | None = None) -> str:
    name = value_or_dash(candidate_name)

    return (
        "❤️ Лайк отправлен.\n\n"
        f"Если {name} тоже нажмет «Нравится», я создам коннект и открою контакт."
    )


def candidate_skipped(candidate_name: str | None = None) -> str:
    name = value_or_dash(candidate_name)

    return (
        f"➡️ {name} пропущен.\n\n"
        "Показываю следующую карточку."
    )


# =========================
# Match / Connect
# =========================

def match_created(
    matched_user: Mapping[str, Any],
    common_interests: Sequence[Any] | None = None,
    greeting: str | None = None,
) -> str:
    name = value_or_dash(matched_user.get("name"))
    username = username_link(matched_user.get("telegram_username"))
    interests = join_items(common_interests or matched_user.get("common_interests"))

    if not greeting:
        greeting = (
            f"Привет! Видел, что у нас совпали интересы: "
            f"{interests}. Может, пообщаемся?"
        )

    return (
        "🎉 <b>У тебя новый коннект!</b>\n\n"
        f"{name} тоже хочет пообщаться с тобой.\n\n"
        f"🤝 <b>Почему вы совпали:</b>\n"
        f"{interests}\n\n"
        f"💬 <b>Telegram:</b>\n"
        f"{username}\n\n"
        f"Идея для первого сообщения:\n"
        f"<i>{h(greeting)}</i>"
    )


def match_notification_for_other_side(
    matched_user: Mapping[str, Any],
    common_interests: Sequence[Any] | None = None,
) -> str:
    return match_created(
        matched_user=matched_user,
        common_interests=common_interests,
    )


MATCH_HIDDEN = (
    "Коннект скрыт."
)

NO_MATCHES = (
    "Пока коннектов нет.\n\n"
    "Нажимай «Искать людей» и ставь лайки тем, кто тебе интересен."
)


# =========================
# Moderation / Safety
# =========================

REPORT_SELECT_REASON = (
    "🚩 <b>Жалоба</b>\n\n"
    "Выбери причину жалобы."
)

REPORT_SENT = (
    "Жалоба отправлена.\n\n"
    "Спасибо, это помогает держать VibeLink безопасным."
)

USER_BLOCKED = (
    "Пользователь заблокирован.\n\n"
    "Он больше не будет попадаться тебе в поиске."
)

BLOCK_CONFIRMATION = (
    "Точно заблокировать этого пользователя?"
)

SAFETY_INFO = (
    "🛡 <b>Безопасность</b>\n\n"
    "Контакт открывается только после взаимного интереса.\n"
    "Ты можешь пожаловаться на пользователя или заблокировать его.\n\n"
    "Не отправляй незнакомым людям документы, деньги, пароли и личные данные."
)


# =========================
# Settings / Filters
# =========================

SETTINGS_MENU = (
    "⚙️ <b>Настройки</b>\n\n"
    "Что хочешь изменить?"
)

FILTERS_MENU = (
    "🎛 <b>Фильтры поиска</b>\n\n"
    "Здесь можно настроить, кого показывать в рекомендациях."
)

FILTERS_SAVED = (
    "✅ Фильтры сохранены."
)

PRIVACY_SAVED = (
    "✅ Настройки приватности сохранены."
)


# =========================
# Dev mocks
# =========================

MOCK_PROFILE: dict[str, Any] = {
    "name": "Твое Имя",
    "age": 23,
    "city": None,
    "is_online": True,
    "goals": ["🎮 Тиммейт", "🧑‍💻 Проекты", "💬 Общение"],
    "interests": ["Cybersecurity", "Backend", "AI", "Minecraft", "GameDev"],
    "communication_formats": ["💬 Переписка", "🎮 Играть вместе", "🧑‍💻 Делать проект"],
    "description": (
        "Люблю ИБ, backend и кооп-игры. Ищу людей для pet-проектов "
        "или вечерних игр. Обычно свободен после 19:00."
    ),
    "looking_for": "Людей на одной волне, тиммейтов и тех, с кем можно делать проекты.",
}

MOCK_CANDIDATE: dict[str, Any] = {
    "id": 2,
    "name": "Имя Кандидата",
    "age": 25,
    "city": None,
    "is_online": False,
    "match_percent": 76,
    "common_interests": ["Minecraft", "Backend", "Кооп-игры"],
    "goals": ["🎮 Тиммейт", "🧑‍💻 Проекты"],
    "description": "Играю по вечерам, интересуюсь backend и хочу делать свои проекты.",
    "looking_for": "Тиммейтов для вечерней игры и людей для pet-проектов.",
    "telegram_username": "vibelink_user",
}


def dev_start_text(telegram_username: str | None = None) -> str:
    username = username_link(telegram_username)

    return (
        f"👋 <b>{BOT_NAME}</b>\n\n"
        "Бот запущен. Сейчас подключен dev-роутер для проверки окружения, "
        "клавиатур и мок-шаблонов.\n\n"
        f"Твой Telegram username: <b>{username}</b>\n\n"
        "Команды для проверки:\n"
        "/ping — проверить ответ бота\n"
        "/mock_profile — мок анкеты\n"
        "/mock_candidate — мок карточки кандидата\n"
        "/mock_match — мок коннекта"
    )