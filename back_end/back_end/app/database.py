import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**DATABASE_CONFIG)

    async def disconnect(self):
        await self.pool.close()

db = Database()
