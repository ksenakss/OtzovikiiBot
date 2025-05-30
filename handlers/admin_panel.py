from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from keyboards.all_keyboards import admin_keyboard, main_keyboard, admins
from db_handler.database_manager import DatabaseManager
from decouple import config
from datetime import datetime, timedelta
import logging

admin_router = Router()

auth_params = {
    'user': config('user'),
    'password': config('password'),
    'host': config('host'),
    'port': config('port'),
    'database': config('database')
}

@admin_router.message(lambda message: message.text == "⚙️ Админ панель")
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id not in admins:
        logging.warning("Non-admin user %s tried to access admin panel", message.from_user.id)
        await message.answer("У вас нет доступа к админ-панели.")
        return

    try:
        logging.info("Admin panel accessed by user %s", message.from_user.id)
        await message.answer("Загрузка статистики...")
        
        db_manager = DatabaseManager(**auth_params)
        async with db_manager as manager:
            try:
                
                total_users = await manager.fetch_data("SELECT COUNT(*) FROM users")
                total_requests = await manager.fetch_data("SELECT COUNT(*) FROM requests")
                total_responses = await manager.fetch_data("SELECT COUNT(*) FROM response")
                
                
                stages_stats = await manager.fetch_data("""
                    SELECT stage, COUNT(*) as count 
                    FROM requests 
                    GROUP BY stage 
                    ORDER BY stage
                """)
                
                
                successful_requests = await manager.fetch_data("""
                    SELECT COUNT(*) 
                    FROM requests 
                    WHERE success = true
                """)
                
                
                last_24h = datetime.now() - timedelta(days=1)
                recent_requests = await manager.fetch_data("""
                    SELECT COUNT(*) 
                    FROM requests 
                    WHERE madeat >= $1
                """, last_24h)
                
                recent_responses = await manager.fetch_data("""
                    SELECT COUNT(*) 
                    FROM response 
                    WHERE created_at >= $1
                """, last_24h)
                
                
                stats_message = (
                    "📊 <b>Статистика бота</b>\n\n"
                    f"👥 Всего пользователей: {total_users[0]['count']}\n"
                    f"🔍 Всего запросов: {total_requests[0]['count']}\n"
                    f"✅ Успешных запросов: {successful_requests[0]['count']}\n"
                    f"📝 Всего ответов: {total_responses[0]['count']}\n\n"
                    "📈 <b>Статистика за последние 24 часа:</b>\n"
                    f"🔍 Новых запросов: {recent_requests[0]['count']}\n"
                    f"📝 Новых ответов: {recent_responses[0]['count']}\n\n"
                    "📊 <b>Распределение по этапам:</b>\n"
                )
                
                
                for stage in stages_stats:
                    stage_name = await manager.fetch_data(
                        "SELECT name FROM vocab_request_stage WHERE id = $1",
                        stage['stage']
                    )
                    stats_message += f"• {stage_name[0]['name']}: {stage['count']}\n"
                
                logging.info("Statistics successfully gathered for user %s", message.from_user.id)
                await message.answer(stats_message, reply_markup=admin_keyboard())
                
            except Exception as e:
                logging.error("Database error in admin panel: %s", str(e))
                await message.answer(f"Ошибка при получении статистики: {str(e)}")
                
    except Exception as e:
        logging.error("General error in admin panel: %s", str(e))
        await message.answer("Произошла ошибка при загрузке админ-панели. Пожалуйста, попробуйте позже.")

@admin_router.message(lambda message: message.text == "📊 Обновить статистику")
async def refresh_stats(message: types.Message, state: FSMContext):
    if message.from_user.id not in admins:
        return
    await admin_panel(message, state)

@admin_router.message(lambda message: message.text == "🔙 Вернуться в главное меню")
async def return_to_main(message: types.Message, state: FSMContext):
    await message.answer("Главное меню", reply_markup=main_keyboard(message.from_user.id))
    await state.clear()