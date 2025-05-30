from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from keyboards.all_keyboards import support_keyboard, main_keyboard
from keyboards.all_keyboards import admins

support_router = Router()

@support_router.message(lambda message: message.text == "🙏 Поддержка")
async def support(message: types.Message, state: FSMContext):
    support_text = (
        "🤖 <b>Центр поддержки</b>\n\n"
        "Здесь вы можете найти ответы на часто задаваемые вопросы и получить помощь:\n\n"
        "📋 <b>Часто задаваемые вопросы:</b>\n"
        "• Как искать товары?\n"
        "  Просто нажмите кнопку '🔍 Найти товар' и введите название интересующего вас товара\n\n"
        "• Как работает анализ отзывов?\n"
        "  Бот собирает отзывы с популярных маркетплейсов и анализирует их с помощью ИИ\n\n"
        "• Почему не все товары находятся?\n"
        "  Бот ищет товары на популярных маркетплейсах. Если товар не найден, попробуйте изменить запрос\n\n"
        "⚠️ <b>Сообщить о проблеме:</b>\n"
        "Нажмите кнопку 'Сообщить о проблеме' ниже, чтобы отправить сообщение разработчикам"
    )
    await message.answer(support_text, reply_markup=support_keyboard())

@support_router.message(lambda message: message.text == "🔙 Вернуться в главное меню")
async def return_to_main(message: types.Message, state: FSMContext):
    await message.answer("Главное меню", reply_markup=main_keyboard(message.from_user.id))
    await state.clear()

@support_router.message(lambda message: message.text == "📝 Сообщить о проблеме")
async def report_issue(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, опишите проблему, с которой вы столкнулись:\n"
        "• Что вы пытались сделать?\n"
        "• Какое сообщение об ошибке вы получили?\n"
        "• На каком этапе возникла проблема?\n\n"
        "Ваше сообщение будет отправлено разработчикам для рассмотрения."
    )
    await state.set_state("waiting_for_issue_description")

@support_router.message(lambda message: message.text == "❓ Как пользоваться ботом")
async def how_to_use(message: types.Message):
    help_text = (
        "📖 <b>Краткое руководство по использованию бота:</b>\n\n"
        "1. Нажмите '🔍 Найти товар'\n"
        "2. Введите название интересующего вас товара\n"
        "3. Подтвердите, что найденный товар - это то, что вы искали\n"
        "4. Дождитесь анализа отзывов\n"
        "5. Получите подробный анализ с плюсами и минусами товара\n\n"
        "💡 <b>Советы:</b>\n"
        "• Используйте точные названия товаров\n"
        "• Можно указывать модель и производителя\n"
        "• Для лучших результатов избегайте общих запросов"
    )
    await message.answer(help_text)

@support_router.message(lambda message: message.text and message.text != "🔙 Вернуться в главное меню" and message.text != "📝 Сообщить о проблеме" and message.text != "❓ Как пользоваться ботом")
async def handle_issue_description(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "waiting_for_issue_description":
        admin_message = (
            f"⚠️ <b>Новое сообщение о проблеме</b>\n\n"
            f"От пользователя: {message.from_user.full_name} (ID: {message.from_user.id})\n"
            f"Сообщение:\n{message.text}"
        )
        
        for admin_id in admins:
            try:
                await message.bot.send_message(admin_id, admin_message, parse_mode="HTML")
            except Exception as e:
                print(f"Failed to send message to admin {admin_id}: {e}")
        
        await message.answer(
            "Спасибо за ваше сообщение! Мы рассмотрим его в ближайшее время.",
            reply_markup=main_keyboard(message.from_user.id)
        )
        await state.clear()