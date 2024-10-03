import datetime
import logging
import json
from datetime import datetime

class RedisConsumer():
    def __init__(self, config):
        self.redis_client = config.redis_client
        self.postgres_pool = config.postgres_pool

        self.keep_alive = True

        self.logger = logging.getLogger(__name__)

        self.REDIS_STREAM = config.REDIS_STREAM
        self.REDIS_BATCH_COUNT = config.REDIS_BATCH_COUNT

    async def consume_redis_stream(self):
        while self.keep_alive:
            messages = await self.redis_client.xread({self.REDIS_STREAM: 0}, block = 0, count=self.REDIS_BATCH_COUNT)
            for _, entries in messages:
                for entry_id, data in entries:
                    decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}

                    await self.process_message(decoded_data)
                    await self.redis_client.xdel(self.REDIS_STREAM, entry_id)

    async def process_message(self, data):
        sensor_type = data.get('type')
        sensor_id = data.get('sensor_id')
        timestamp = data.get('timestamp')

        if not timestamp:
            timestamp = datetime.now()
        else:
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError as e:
                self.logger.error(f"Invalid timestamp format: {timestamp}, Error: {e}")
                return


        data_fields = data.get('data_fields')

        if sensor_id is None or sensor_type is None or data_fields is None:
            self.logger.error(f"Invalid message data: sensor_id={sensor_id}, sensor_type={sensor_type}")
            return  # Skip this message and do not process it
        
        
        
        data_fields_json = json.dumps(data_fields)

        await self.store_data(sensor_id, sensor_type, timestamp, data_fields_json)

    async def store_data(self, sensor_id, sensor_type, timestamp, data_fields):
        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                query = """
                    INSERT INTO sensor_data (sensor_id, sensor_type, timestamp, data)
                    VALUES ($1, $2, $3, $4)
                """

                await conn.execute(query, 
                    sensor_id,
                    sensor_type,
                    timestamp,
                    data_fields
                )