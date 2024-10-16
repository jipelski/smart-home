import logging
import json
from datetime import datetime
from redis.asyncio import Redis
import os
import asyncpg
import asyncio
from dotenv import load_dotenv
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RedisToDB():
    def __init__(self):
        load_dotenv()
        self.redis_client = Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
        self.REDIS_STREAM = os.getenv('REDIS_STREAM')
        self.REDIS_BATCH_COUNT = int(os.getenv('REDIS_BATCH_COUNT'))

        self.keep_alive = True

        logging.basicConfig(
            filename=os.getenv('LOG_FILE'),
            format=os.getenv('LOG_FORMAT'), 
            datefmt=os.getenv('LOG_DATE_FORMAT') , 
            encoding=os.getenv('LOG_ENCODING'), 
            level=logging.DEBUG
        )
        self.logger = logging.getLogger(__name__)

    async def init_postgres(self):
        self.postgres_pool = await asyncpg.create_pool(
            database = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )

    async def start(self):
        while self.keep_alive:
            messages = await self.redis_client.xread({self.REDIS_STREAM: 0}, block = 5000, count=self.REDIS_BATCH_COUNT)
            for _, entries in messages:
                for entry_id, data in entries:
                    decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}

                    await self.process_message(decoded_data)
                    await self.redis_client.xdel(self.REDIS_STREAM, entry_id)

    async def process_message(self, data):
        try:
            sensor_type = data.get('type')
            sensor_id = data.get('sensor_id')
            timestamp = data.get('timestamp')
        except Exception as e:
            self.logger.error(f'Expected keys not found in data: {data} - {e}')
            return #pass

        if not timestamp:
            timestamp = datetime.now()
        else:
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError as e:
                self.logger.error(f"Invalid timestamp format: {timestamp}, Error: {e}")
                return


        data_fields = json.loads(data.get('data_fields'))
        for key, value in data_fields.items():
            if isinstance(value, float):
                data_fields[key] = round(value, 2)

        if sensor_id is None or sensor_type is None or data_fields is None:
            self.logger.error(f"Invalid message data: sensor_id={sensor_id}, sensor_type={sensor_type}")
            return  # Skip this message and do not process it
        
        
        await self.store_data(sensor_id, sensor_type, timestamp, data_fields)

    async def store_data(self, sensor_id : str, sensor_type : str, timestamp : datetime, data_fields : json):
        table_name = sensor_type

        columns = ['sensor_id', 'timestamp'] + list(data_fields.keys())
        values = [sensor_id, timestamp] + list(data_fields.values())

        place_holders = ','.join([f'${i+1}' for i in range(len(values))])
        columns_str = ','.join(columns)

        query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({place_holders})
        """

        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, *values)
        try:
            channel = f'sensor_updates:{sensor_id}'
            await self.redis_client.publish(channel=channel, message=data_fields)
        except Exception as e:
            self.logger.exception(f'Failed to publish message to Redis: {e}')

    async def close(self):
        await self.redis_client.aclose()
        await self.postgres_pool.close()

async def main():
    service = RedisToDB()
    await service.init_postgres()
    try:
        await service.start()
    finally:
        await service.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user")