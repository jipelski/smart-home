import logging
import struct
import json
import asyncio_mqtt
import asyncio
from ble_client import BLE_Client
from config import Config

class HubManager():
    def __init__(self):
        self.config = Config()

        self.mqtt_client = asyncio_mqtt.Client(
            hostname=self.config.MQTT_BROKER,
            port=self.config.MQTT_PORT,
            username=self.config.MQTT_USERNAME,
            password=self.config.MQTT_PASSWORD,
        )

        logging.basicConfig(
            filename=self.config.BLE_LOG_FILE, 
            format=self.config.BLE_LOG_FORMAT, 
            datefmt=self.config.BLE_LOG_DATE_FORMAT , 
            encoding=self.config.BLE_LOG_ENCODING, 
            level=logging.DEBUG
        )

        self.logger = logging.getLogger("HubManager")
        self.clients = {}
        self.start_mqtt()

    async def start_mqtt(self):
        try:
            await self.mqtt_client.connect()
            await self.mqtt_client.subscribe(self.config.MQTT_COMMAND_TOPIC)
        except Exception as e:
            self.logger.exception(f'Failed to start mqtt client: {e}')


    async def create_and_connect(self, peripheral_mac, service_uuid, characteristic_uuid, structure):
        client = BLE_Client(
            logger=self.logger, 
            peripheral_mac=peripheral_mac, 
            service_uuid=service_uuid, 
            characteristic_uuid=characteristic_uuid, 
            structure=structure,
            handler=self.handle_data
        )
        await client.connect()
        self.clients[peripheral_mac] = client

    async def disconnect_ble_client(self, peripheral_mac):
        client = self.clients[peripheral_mac]
        await client.disconnect()
        try:
            del self.clients[peripheral_mac]
        except Exception as e:
            self.logger.exception(f'{peripheral_mac} not in client dictionary: {e}')

    def handle_data(self, structure, peripheral_mac, data):
        try:
            unpacked_data = struct.unpack(structure, data)
            final_data = (peripheral_mac,) + unpacked_data
            asyncio.create_task(self.send_data_to_backend(final_data))
        except Exception as e:
            self.logger.exception(f'Unable to unpack data from {peripheral_mac} - {e}')

    async def send_data_to_backend(self, data):
        try:
            topic = self.config.MQTT_DATA_TOPIC
            payload = json.dumps(data)
            await self.mqtt_client.publish(topic, payload)
        except Exception as e:
            self.logger.exception(f"Failed to send data: {e}")

    async def handle_commands(self):
        try:
            async with self.mqtt_client.unfiltered_messages() as messages:
                async for message in messages:
                    payload = json.loads(message.payload.decode())
                    command = payload.get("command")
                    if command == "connect_device":
                        await self.create_and_connect(
                            payload["peripheral_mac"],
                            payload["service_uuid"],
                            payload["characteristic_uuid"],
                            payload["structure"],
                        )
                    elif command == "disconnect_device":
                        await self.disconnect_ble_client(payload["peripheral_mac"])
        except Exception as e:
            self.logger.exception(f'Failed to handle commands: {e}')