import os
import json
import aiomqtt

MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_COMMAND_TOPIC_BASE = os.getenv('COMMAND_TOPICS', 'command/hub')

async def publish_command(hub_id: str, command: dict):
    topic = f"{MQTT_COMMAND_TOPIC_BASE}/{hub_id}"
    async with aiomqtt.Client(
        hostname=MQTT_BROKER, 
        port=MQTT_PORT,
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD,
        keepalive=20
    ) as client:
        await client.publish(
            topic=topic,
            payload=json.dumps(command),
            qos=2
        )