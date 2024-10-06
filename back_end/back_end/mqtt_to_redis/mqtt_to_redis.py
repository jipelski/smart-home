import aiomqtt
import asyncio
import json
import os
from redis.asyncio import Redis
import logging
from dotenv import load_dotenv
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class MqttToRedis():
    def __init__(self):
        load_dotenv()
        logging.basicConfig(
            filename=os.getenv('LOG_FILE'),
            format=os.getenv('LOG_FORMAT'), 
            datefmt=os.getenv('LOG_DATE_FORMAT') , 
            encoding=os.getenv('LOG_ENCODING'), 
            level=logging.DEBUG
        )
        self.logger = logging.getLogger(__name__)

        self.DATA_TOPICS = set(os.getenv('DATA_TOPICS').split(','))

        self.mqtt_client = aiomqtt.Client(
            hostname=os.getenv('MQTT_BROKER'), 
            port=int(os.getenv('MQTT_PORT')),
            username=os.getenv('MQTT_USERNAME'),
            password=os.getenv('MQTT_PASSWORD'),
            keepalive=int(os.getenv('MQTT_ALIVE_INTERVAL'))
        )

        self.redis_client = Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

        self.REDIS_STREAM = os.getenv('REDIS_STREAM')
    
    async def start(self):
        while True:
            try:
                async with self.mqtt_client:
                    self.logger.info("MQTT client connected")
                    for topic in self.DATA_TOPICS:
                        self.logger.info(f"Subscribing to {topic}")
                        await self.mqtt_client.subscribe(topic)
                    await self.handle_data()
            except Exception as e:
                self.logger.exception(f'Failed to maintain MQTT connection: {e}')
                return

    async def handle_data(self):
        async for message in self.mqtt_client.messages:
            try:
                message_payload = message.payload.decode('utf-8')
        
                message_dict = json.loads(message_payload)
                # Convert the `data_fields` dict to a JSON string
                if 'data_fields' in message_dict:
                    message_dict['data_fields'] = json.dumps(message_dict['data_fields'])
                
                await self.redis_client.xadd(self.REDIS_STREAM, message_dict)

            except Exception as e:
                self.logger.exception(f'Unable to add message to redis stream: {e}')

async def main():
    service = MqttToRedis()
    await service.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user")