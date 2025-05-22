import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_handler.main_handler import PostgresHandler
from aiogram import Router, types
from handlers.start import start_router
from handlers.about import about_router
from handlers.support import support_router
from handlers.admin_panel import admin_router
from keyboards.all_keyboards import admins


# Настройки логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def main():
    # Инициализация базы данных
    await PostgresHandler(config('PG_LINK'))

    dp.include_router(start_router)
    dp.include_router(about_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    # Удаление вебхука (если он есть) и запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
