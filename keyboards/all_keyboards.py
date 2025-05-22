from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Список админов (заменяем импорт из cache.config)
admins = [123456789]  # Замените на реальные ID администраторов

def main_keyboard(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text="🔍 Найти товар")],
        [KeyboardButton(text="📖 О нас"), KeyboardButton(text="🙏 Поддержка")]
    ]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню"
        )
    return keyboard

def inline_keyboard_for_approve():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="yes"),
                InlineKeyboardButton(text="Нет", callback_data="no")
            ]
        ]
    )
    return keyboard