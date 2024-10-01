import asyncio_mqtt

class MqttManager():
    def __init__(self, config):
        self.logger = config.logger

        self.DATA_TOPICS = set(config.DATA_TOPICS)
        self.COMMDAND_TOPICS = set(config.COMMAND_TOPICS)

        self.redis_client = config.redis_client
        self.REDIS_STREAM = config.REDIS_STREAM

        self.mqtt_client = asyncio_mqtt.Client(
            hostname=config.MQTT_BROKER, 
            port=config.MQTT_PORT, 
            username=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
        )
    
    async def start_mqtt(self):
        try:
            await self.mqtt_client.connect()
            for topic in self.DATA_TOPICS:
                try:
                    await self.mqtt_client.subscribe(topic)
                except Exception as e:
                    self.logger.exception(f'Failed to subscribe to data topic: {topic} - {e}')
        except Exception as e:
            self.logger.exception(f'Failed to start mqtt client: {e}')

    async def register_topic(self, topic, type):
        match(type):
            case 'command':
                self.COMMDAND_TOPICS.add(topic)
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
                    self.COMMDAND_TOPICS.remove(topic)
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
            if command_topic in self.COMMDAND_TOPICS:
                await self.mqtt_client.publish(topic=command_topic, payload=command_data, qos=2)
            else:
                self.logger.error(f'Unable to publish to topic: {command_topic} - topic not registered in topics set')
        except Exception as e:
            self.logger.exception(f'Unable to publish to topic: {command_topic} - {e}')

    async def handle_data(self):
        try:
            async with self.mqtt_client.messages() as messages:
                async for message in messages:
                    try:
                        self.redis_client.xadd(self.REDIS_STREAM, message)
                    except Exception as e:
                        self.logger.exception(f'Unable to add message to redis stream: {e}')
        except Exception as e:
            self.logger.exception(f'Unable to handle data: {e}')
