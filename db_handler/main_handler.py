import logging
from decouple import config
from db_handler.database_manager import DatabaseManager
from db_handler.table_config import TABLES_CONFIG
import asyncio

auth_params = {
    'user': config('user'),
    'password': config('password'),
    'host': config('host'),
    'port': config('port'),
    'database': config('database')
}

async def PostgresHandler(pg_link):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        # Создаем все таблицы из конфигурации
        for table_name, table_config in TABLES_CONFIG.items():
            # Создаем таблицу
            await manager.create_table(table_name, table_config["columns"])
            logging.info(f"Таблица {table_name} создана: {table_config['description']}")
            
            # Создаем индексы, если они есть
            if "indexes" in table_config:
                for index_query in table_config["indexes"]:
                    await manager.fetch_data(index_query)
                    logging.info(f"Индекс создан для таблицы {table_name}")
            
            # Заполняем начальными данными, если они есть
            if "initial_data" in table_config:
                for data in table_config["initial_data"]:
                    # Проверяем, есть ли уже такие данные
                    check_query = f"SELECT * FROM {table_name} WHERE codeName = $1"
                    existing = await manager.fetch_data(check_query, data["codeName"])
                    if not existing:
                        await manager.insert_data(table_name, data)
                        logging.info(f"Добавлены начальные данные в таблицу {table_name}")

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
        if not numberOfRequest:
            logging.error(f"No request found for user {user_id}")
            return
        await manager.update_data("requests", "stage", newValue, "id = $2", numberOfRequest[0]["id"])
        logging.info(f"Updated stage to {newValue} for request {numberOfRequest[0]['id']}")

async def updateNameRequestByUserId(newValue, user_id):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        query = """SELECT id FROM requests WHERE user_id = $1 ORDER BY madeat DESC LIMIT 1"""
        numberOfRequest = await manager.fetch_data(query, user_id)
        if not numberOfRequest:
            logging.error(f"No request found for user {user_id}")
            return
        await manager.update_data("requests", "name", newValue, "id = $2", numberOfRequest[0]["id"])
        logging.info(f"Updated name to {newValue} for request {numberOfRequest[0]['id']}")

async def addResponse(data):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        await manager.insert_data("response", data)

async def getResponseByRequestId(request_id):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        query = "SELECT * FROM response WHERE request_id = $1 ORDER BY created_at DESC LIMIT 1"
        return await manager.fetch_data(query, request_id)

async def getResponsesByUserId(user_id):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
        query = "SELECT * FROM response WHERE user_id = $1 ORDER BY created_at DESC"
        return await manager.fetch_data(query, user_id)










