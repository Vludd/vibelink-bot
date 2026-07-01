from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Переиспользуемые «одиночные» клавиатуры
REMOVE = ReplyKeyboardRemove()


def _kb(*rows: list[str], resize: bool = True, one_time: bool = False) -> ReplyKeyboardMarkup:
    """Хелпер: принимает список рядов строк → ReplyKeyboardMarkup."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=resize,
        one_time_keyboard=one_time,
    )


# ──────────────────────── онбординг ────────────────────────

def kb_skip() -> ReplyKeyboardMarkup:
    """Универсальная кнопка пропуска (фото, описание…)."""
    return _kb(["⏭ Пропустить"], one_time=True)


def kb_skip_or_remove_photo() -> ReplyKeyboardMarkup:
    return _kb(["⏭ Пропустить"], ["🗑 Удалить фото"], one_time=True)


def kb_confirm_city() -> ReplyKeyboardMarkup:
    """Показываем, когда пользователь ввёл город — просим подтвердить или ввести заново."""
    return _kb(["✅ Верно"], ["✏️ Изменить"], one_time=True)