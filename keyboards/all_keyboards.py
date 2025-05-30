from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

admins = [432970861]

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

def support_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❓ Как пользоваться ботом"),
                KeyboardButton(text="📝 Сообщить о проблеме")
            ],
            [
                KeyboardButton(text="🔙 Вернуться в главное меню")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Обновить статистику")
            ],
            [
                KeyboardButton(text="🔙 Вернуться в главное меню")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard