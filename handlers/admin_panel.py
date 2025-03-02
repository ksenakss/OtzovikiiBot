from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from openai import OpenAI

admin_router = Router()

# Обработчик нажатия кнопки "🔍 Найти товар"
@admin_router.message(lambda message: message.text == "⚙️ Админ панель")
async def about(message: types.Message, state: FSMContext):
    await message.answer("Админ панель в разработке")