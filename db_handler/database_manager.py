import asyncpg
import logging
from decouple import config

class DatabaseManager:
    def __init__(self, user, password, database, host, port):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.connection = None

    async def __aenter__(self):
        self.connection = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port,
            min_size=5,
            max_size=20
        )
        logging.info("Database connection pool established.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.connection.close()
        logging.info("Database connection pool closed.")

    async def create_table(self, table_name: str, columns: dict):
        columns_with_types = ", ".join([f"{name} {type}" for name, type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types});"
        async with self.connection.acquire() as conn:
            await conn.execute(query)
        logging.info(f"Table {table_name} created with columns {columns}.")

    async def insert_data(self, table_name: str, data: dict):
        if table_name == "reviews_cache":
            check_query = "SELECT item_title FROM reviews_cache WHERE item_title = $1"
            async with self.connection.acquire() as conn:
                existing = await conn.fetch(check_query, data.get('item_title'))
                if existing:
                    update_parts = [f"{k} = ${i+2}" for i, k in enumerate(data.keys())]
                    update_query = f"UPDATE {table_name} SET {', '.join(update_parts)} WHERE item_title = $1"
                    await conn.execute(update_query, data.get('item_title'), *[v for v in data.values()])
                    logging.info(f"Updated existing record in {table_name}: {data}")
                    return

        columns = ", ".join(data.keys())
        values = ", ".join(f"${i+1}" for i in range(len(data)))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        async with self.connection.acquire() as conn:
            await conn.execute(query, *data.values())

    async def fetch_data(self, query: str, *args):
        async with self.connection.acquire() as conn:
            rows = await conn.fetch(query, *args)
        return rows

    async def update_data(self, table_name: str, column_name: str, new_value, condition: str, *condition_args):
        query = f"UPDATE {table_name} SET {column_name} = $1 WHERE {condition};"
        async with self.connection.acquire() as conn:
            await conn.execute(query, new_value, *condition_args)
        logging.info(f"Data updated in {table_name}: {column_name} = {new_value} WHERE {condition}.")
    
    async def update_boolean_data(self, table_name: str, column_name: str, new_value, condition: str, *condition_args):
        query = f"UPDATE {table_name} SET {column_name} = $1 WHERE {condition};"
        async with self.connection.acquire() as conn:
            await conn.execute(query, new_value, *condition_args)
        logging.info(f"Data updated in {table_name}: {column_name} = {new_value} WHERE {condition}.")

auth_params = {
    'user': config('user'),
    'password': config('password'),
    'database': config('database'),
    'host': config('host'),
    'port': config('port')
}