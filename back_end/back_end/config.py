from dotenv import load_dotenv
import os
import logging
import asyncpg
import redis.asyncio as aioredis

class Config():
    def __init__(self):
        load_dotenv()

        logging.basicConfig(
            filename=os.getenv('APP_LOG_FILE'),
            format=os.getenv('APP_LOG_FORMAT'), 
            datefmt=os.getenv('APP_LOG_DATE_FORMAT') , 
            encoding=os.getenv('APP_LOG_ENCODING'), 
            level=logging.DEBUG
        )

        self.DATA_TOPICS = set(os.getenv('DATA_TOPICS').split(','))
        self.COMMAND_TOPICS = set(os.getenv('COMMAND_TOPICS').split(','))
        self.MQTT_BROKER = os.getenv('MQTT_BROKER')
        self.MQTT_PORT = int(os.getenv('MQTT_PORT'))
        self.MQTT_ALIVE_INTERVAL = int(os.getenv('MQTT_ALIVE_INTERVAL'))
        self.MQTT_USERNAME = os.getenv('MQTT_USERNAME')
        self.MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

        self.redis_client = aioredis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
        self.REDIS_STREAM = os.getenv('REDIS_STREAM')
        self.REDIS_BATCH_COUNT = int(os.getenv('REDIS_BATCH_COUNT'))

        self.logger = logging.getLogger(__name__)

        
        for topic in self.DATA_TOPICS:
            self.logger.info(f"Config topic:{topic}")

    async def init_postgres(self):
        self.postgres_pool = await asyncpg.create_pool(
            database = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )