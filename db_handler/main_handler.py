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

async def PostgresHandler(pg_link):
    db_manager = DatabaseManager(**auth_params)
    async with db_manager as manager:
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


# loop = asyncio.get_event_loop()
# loop.run_until_complete(PostgresHandler(config('PG_LINK')))

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










