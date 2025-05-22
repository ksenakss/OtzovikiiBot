import logging
from decouple import config
from db_handler.database_manager import DatabaseManager
import asyncio

auth_params = {
    'user': config('user'),
    'password': config('password'),
    'host': config('host'),
    'port': config('port'),
    'database': config('database')
}

async def recreate_reviews_cache_table():
    """Пересоздает таблицу для кэша отзывов с новыми колонками"""
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        # Удаляем старую таблицу
        async with manager.connection.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS reviews_cache;")
        # Создаем новую таблицу
        await manager.create_reviews_cache_table()
        print("Таблица reviews_cache пересоздана с новыми колонками.")

async def cleanup_duplicate_reviews():
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        await manager.cleanup_duplicate_reviews()
        print("Duplicate reviews cleaned up.")

async def PostgresHandler(pg_link):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        # Пересоздаем таблицу для кэша отзывов
        await recreate_reviews_cache_table()
        print("Таблица reviews_cache пересоздана.")

        # Очищаем дублирующиеся записи
        await cleanup_duplicate_reviews()
        print("Дублирующиеся записи очищены.")

        columns = {
            "id": "BIGINT PRIMARY KEY",
            "name": "VARCHAR(255)",
            "requests": "BIGINT"
        }
        await manager.create_table("users", columns)
        print("Таблица users создана.")
        
        columns = {
            "id": "BIGSERIAL PRIMARY KEY",
            "codeName": "varchar",
            "name": "VARCHAR(255)"
        }
        await manager.create_table("vocab_request_stage", columns)
        print("Таблица vocab_request_stage создана.")
        
        codeStages = [
            "requestForTitle",
            "lookForTitle",
            "checkIfRight",
            "lookForReviewsAndPrices"
        ]
        stages = [
            "Запрос поиска",
            "Поиск по названию",
            "Проверка верности поиска",
            "Поиск отзывов и цен",
        ]
        for i in range(len(codeStages)):
            query = "SELECT * FROM vocab_request_stage"
            vocab = await manager.fetch_data(query)
            if len(vocab) == 0:
                await manager.insert_data("vocab_request_stage",
                {
                    "codeName": codeStages[i],
                    "name": stages[i]
                })

        print("Таблица vocab_requests создана.")
        columns = {
            "id": "BIGSERIAL PRIMARY KEY",
            "name": "VARCHAR(255)",
            "madeAt": "TIMESTAMP",
            "success": "boolean",
            "stage": "BIGINT REFERENCES vocab_request_stage(id)",
            "user_id": "BIGINT REFERENCES users(id) ON DELETE CASCADE"
        }
        await manager.create_table("requests", columns)
        print("Таблица requests создана.")

# Добавляем новые функции для работы с кэшем
async def get_cached_reviews(item_title: str):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        return await manager.get_cached_reviews(item_title)

async def cache_reviews(item_title: str, user_query: str = None, product_url: str = None,
                       wb_reviews=None, ozon_reviews=None, yandex_reviews=None, 
                       gpt_analysis=None, ttl_days=7):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        await manager.cache_reviews(
            item_title=item_title,
            user_query=user_query,
            product_url=product_url,
            wb_reviews=wb_reviews,
            ozon_reviews=ozon_reviews,
            yandex_reviews=yandex_reviews,
            gpt_analysis=gpt_analysis,
            ttl_days=ttl_days
        )

async def clear_expired_cache():
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        await manager.clear_expired_cache()

# Остальные функции остаются без изменений
async def insertInUsers(data):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        user_id = data["id"]
        query = "SELECT * FROM users WHERE id = $1"
        user = await manager.fetch_data(query, user_id)
        if len(user) == 0:
            await manager.insert_data("users", data)

async def addRequest(data):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        await manager.insert_data("requests", data)

async def updateStageRequestByUserId(newValue, user_id):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        query = """SELECT id FROM requests WHERE user_id = $1 ORDER BY madeat DESC LIMIT 1"""
        numberOfRequest = await manager.fetch_data(query, user_id)
        await manager.update_data("requests", "stage", newValue, "id = $2", numberOfRequest[0]["id"])

async def updateNameRequestByUserId(newValue, user_id):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        query = """SELECT id FROM requests WHERE user_id = $1 ORDER BY madeat DESC LIMIT 1"""
        numberOfRequest = await manager.fetch_data(query, user_id)
        await manager.update_data("requests", "name", newValue, "id = $2", numberOfRequest[0]["id"])










