import datetime
import psycopg2
from psycopg2 import sql, extras

class RedisConsumer():
    def __init__(self, config):
        self.redis_client = config.redis_client
        self.postgres_conn = config.postgres_conn

        self.keep_alive = True
        self.logger = config.logger

        self.REDIS_STREAM = config.REDIS_STREAM
        self.REDIS_BATCH_COUNT = config.REDIS_BATCH_COUNT
        self.POSTGRES_BATCH_MAX = config.POSTGRES_BATCH_MAX
        self.inserts = 0

    def consume_redis_stream(self):
        while self.keep_alive:
            try:
                messages = self.redis_client.xread({self.REDIS_STREAM: 0}, block = 0, count=self.REDIS_BATCH_COUNT)
                for _, entries in messages:
                    for entry_id, data in entries:
                        self.process_message(data)
                        self.redis_client.xdel(self.REDIS_STREAM, entry_id)

            except Exception as e:
                self.logger.exception(f'Could not consume messages: {e}')

    def process_message(self, data):
        try:
            sensor_type = data.get('type')
            sensor_id = data.get('sensor_id')
            timestamp = data.get('timestamp')

            if not timestamp:
                timestamp = datetime.utcnow()

            data_fields = data.get('data_fields')

            self.store_data(sensor_id, sensor_type, timestamp, data_fields)
        except Exception as e:
            self.logger.exception(f'Could not process data: {e}')

    def store_data(self, sensor_id, sensor_type, timestamp, data_fields):
        try:
            with self.postgres_conn.cursor() as cursor:
                query = """
                    INSERT INTO sensor_data (sensor_id, sensor_type, timestamp, data)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    sensor_id,
                    sensor_type,
                    timestamp,
                    extras.Json(data_fields)
                ))
                self.inserts += 1
            if(self.inserts >= self.POSTGRES_BATCH_MAX):
                try:
                    self.postgres_conn.commit()
                    self.inserts = 0
                except Exception as e:
                    self.logger.exception(f'Could not commit to database: {e}')    
        except Exception as e:
            self.logger.exception(f'Could not store data: {e}')