import struct
import json
import aiomqtt
import asyncio
from ble_client import BLEClient
import datetime

class HubManager():
    def __init__(self, config):
        self.config = config
        
        self.LOOK_UP_TABLE = config.LOOK_UP_TABLE

        self.MQTT_DATA_TOPIC = config.MQTT_DATA_TOPIC

        self.logger = config.logger

        self.mqtt_client = aiomqtt.Client(
            hostname=config.MQTT_BROKER, 
            port=int(config.MQTT_PORT),
            username=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
            identifier=config.MQTT_IDENTIFIER,
            keepalive=20
        )

        self.clients = {}

    async def start_mqtt(self):
        while True:
            try:
                async with self.mqtt_client:
                    self.logger.info("MQTT client connected")
                    await self.mqtt_client.subscribe(self.config.MQTT_COMMAND_TOPIC)
                    await self.handle_commands()
            except Exception as e:
                self.logger.exception(f'Failed to start or maintain mqtt connection: {e}')
                await asyncio.sleep(5)


    async def create_and_connect(self, peripheral_mac, service_uuid, characteristic_uuid, structure, type):
        client = BLEClient(
            logger=self.logger, 
            peripheral_mac=peripheral_mac, 
            service_uuid=service_uuid, 
            characteristic_uuid=characteristic_uuid, 
            structure=structure,
            handler=self.handle_data,
            type=type
        )
        await client.connect()
        self.clients[peripheral_mac] = client

    async def disconnect_ble_client(self, peripheral_mac):
        try:
            client = self.clients.pop(peripheral_mac)
            await client.disconnect()
        except KeyError:
            self.logger.error(f'{peripheral_mac} not in client dictionary')
        except Exception as e:
            self.logger.exception(f'Unable to disconnect client: {e}')

    def handle_data(self, structure, peripheral_mac, type, data):
        try:
            unpacked_data = struct.unpack(structure, data)
            date = datetime.datetime(*unpacked_data[:6]).isoformat()
            json_data = { 'type': type , 'sensor_id': peripheral_mac, 'timestamp': date}
            data_fields = {}
            for attr, index in self.LOOK_UP_TABLE.get(type).items():
                data_fields[attr] = unpacked_data[index]
            json_data['data_fields'] = data_fields
            asyncio.create_task(self.send_data_to_backend(json_data))
        except Exception as e:
            self.logger.exception(f'Unable to unpack data from {peripheral_mac} - {e}')

    async def send_data_to_backend(self, data):
        try:
            payload = json.dumps(data)
            await self.mqtt_client.publish(topic=self.MQTT_DATA_TOPIC, payload=payload, qos=2)
        except Exception as e:
            self.logger.exception(f"Failed to send data: {e}")

    async def handle_commands(self):
        try:
            async for message in self.mqtt_client.messages:    
                try:
                    payload = json.loads(message.payload.decode())
                    command = payload.get("command")
                    if command == "connect_device":
                        await self.create_and_connect(
                            payload["peripheral_mac"],
                            payload["service_uuid"],
                            payload["characteristic_uuid"],
                            payload["structure"],
                            payload["type"],
                        )
                    elif command == "disconnect_device":
                        await self.disconnect_ble_client(payload["peripheral_mac"])
                    else:
                        self.logger.error(f'Unknown command received: {command}')
                except Exception as e:
                    self.logger.exception(f'Failed to handle commands: {e}')
        except asyncio.CancelledError as e:
            self.logger.exception("Task was cancelled. Cleaning up...")
            raise e