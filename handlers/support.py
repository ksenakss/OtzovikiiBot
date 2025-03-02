from aiogram import Router, types
from aiogram.fsm.context import FSMContext

support_router = Router()

# Обработчик нажатия кнопки "🔍 Найти товар"
@support_router.message(lambda message: message.text == "🙏 Поддержка")
async def about(message: types.Message, state: FSMContext):
    await message.answer("Поддержка в разработке")