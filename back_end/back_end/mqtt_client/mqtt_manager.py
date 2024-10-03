import aiomqtt
import asyncio
import logging
import json

class MqttManager():
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.DATA_TOPICS = set(config.DATA_TOPICS)
        self.COMMAND_TOPICS = set(config.COMMAND_TOPICS)

        self.mqtt_client = aiomqtt.Client(
            hostname=config.MQTT_BROKER, 
            port=config.MQTT_PORT,
            username=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
            keepalive=config.MQTT_ALIVE_INTERVAL
        )

        self.redis_client = config.redis_client
        self.REDIS_STREAM = config.REDIS_STREAM
    
    async def start_mqtt(self):
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
                await asyncio.sleep(5)

    async def register_topic(self, topic, type):
        match(type):
            case 'command':
                self.COMMAND_TOPICS.add(topic)
            case 'data':
                self.DATA_TOPICS.add(topic)
                try:
                    await self.mqtt_client.subscribe(topic=topic)
                except Exception as e:
                    self.logger.exception(f'Unable to subscribe to topic: {topic} - {e}')
            case _:
                self.logger.error(f'Invalid topic type: {type}')

    async def unregister_topic(self, topic, type):
        match(type):
            case 'command':
                try:
                    self.COMMAND_TOPICS.remove(topic)
                except Exception as e:
                    self.logger.exception(f'Topic could not be removed: {topic} - {type} - {e}')
            case 'data':
                try:
                    await self.mqtt_client.unsubscribe(topic=topic)
                except Exception as e:
                    self.logger.exception(f'Topic could not be unsubscribed from: {topic} - {type} - {e}')
                try:
                    self.DATA_TOPICS.remove(topic)
                except Exception as e:
                    self.logger.exception(f'Topic could not be removed: {topic} - {type} - {e}')

    async def publish_command(self, command_topic, command_data):
        try:
            if command_topic in self.COMMAND_TOPICS:
                await self.mqtt_client.publish(topic=command_topic, payload=command_data, qos=2)
            else:
                self.logger.error(f'Unable to publish to topic: {command_topic} - topic not registered in topics set')
        except Exception as e:
            self.logger.exception(f'Unable to publish to topic: {command_topic} - {e}')

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
