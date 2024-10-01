from dotenv import load_dotenv
import os
import logging
import psycopg2
import redis

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

        self.COMMAND_TOPICS = os.getenv('COMMAND_TOPICS')
        self.DATA_TOPICS = os.getenv('DATA_TOPICS')
        self.MQTT_BROKER = os.getenv('MQTT_BROKER')
        self.MQTT_PORT = os.getenv('MQTT_PORT')
        self.MQTT_USERNAME = os.getenv('MQTT_USERNAME')
        self.MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

        # TODO create a redis client  
        self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
        self.REDIS_STREAM = os.getenv('REDIS_STREAM')
        self.REDIS_BATCH_COUNT = os.getenv('REDIS_BATCH_COUNT')

        # TODO create postgres client and connect to it 
        self.postgres_conn = psycopg2.connect(
            dbname = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )
        self.POSTGRES_BATCH_MAX = os.getenv('POSTGRES_BATCH_MAX')

        self.logger = logging.getLogger("APP")