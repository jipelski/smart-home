import struct
import json
import asyncio_mqtt
import asyncio
from ble_client import BLEClient
import datetime
from config import Config

class HubManager():
    def __init__(self, config):
        self.mqtt_client = asyncio_mqtt.Client(
            hostname=config.MQTT_BROKER,
            port=config.MQTT_PORT,
            username=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
        )
        
        self.LOOK_UP_TABLE = config.LOOK_UP_TABLE

        self.logger = config.logger
        self.clients = {}

    # TODO: ensure client stays connected by wrapping start_mqtt command call into a loop that listens and excepts aimqtt.errors
    async def start_mqtt(self):
        try:
            await self.mqtt_client.connect()
            await self.mqtt_client.subscribe(self.config.MQTT_COMMAND_TOPIC)
        except Exception as e:
            self.logger.exception(f'Failed to start mqtt client: {e}')


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
            client = self.clients[peripheral_mac]
            await client.disconnect()
            try:
                del self.clients[peripheral_mac]
            except KeyError:
                self.logger.exception(f'{peripheral_mac} not in client dictionary: {e}')
        except Exception as e:
            self.logger.exception(f'Unable to disconnect client: {e}')

    def handle_data(self, structure, peripheral_mac, type, data):
        try:
            unpacked_data = struct.unpack(structure, data)
            date = datetime(unpacked_data[0], unpacked_data[1], unpacked_data[2], unpacked_data[3], unpacked_data[4], unpacked_data[5])
            json_data = { 'type' : type , 'sensor_id' : peripheral_mac, 'timestamp' : date}
            data_fields = {}
            for attribute, index in self.LOOK_UP_TABLE.get(type):
                data_fields[attribute] = unpacked_data[index]
            json_data['data_fields'] = data_fields
            asyncio.create_task(self.send_data_to_backend(json_data))
        except Exception as e:
            self.logger.exception(f'Unable to unpack data from {peripheral_mac} - {e}')

    # TODO: implement sending data through ssl by creating tsl parameters and encrypt it using a cypher
    async def send_data_to_backend(self, data):
        try:
            topic = self.config.MQTT_DATA_TOPIC
            qos = 2 # QOS 2 ensures the message is sent exactly once
            payload = json.dumps(data)
            await self.mqtt_client.publish(topic=topic, payload=payload, qos=qos)
        except Exception as e:
            self.logger.exception(f"Failed to send data: {e}")

    # TODO: ensure messages are sent using tsl_parameters and decypher accordingly
    async def handle_commands(self):
        try:
            async with self.mqtt_client.messages() as messages:
                async for message in messages:
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