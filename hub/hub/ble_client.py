from bleak import BleakClient

class BLE_Client():
    def __init__(self, logger, peripheral_mac, service_uuid, characteristic_uuid, structure, handler):
        self.logger = logger
        self.client = BleakClient(peripheral_mac)
        self.peripheral_mac = peripheral_mac
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.structure = structure
        self.connected = False
        self.handler = handler
    
    def notification_handler(self, sender, data):
        self.handler(self.structure, self.peripheral_mac, data)
    
    async def connect(self):
        try:
            await self.client.connect()
            self.connected = True
            self.logger.info(f"Connected to {self.client.address}")
            await self.subscribe()
        except Exception as e:
            self.connected = False
            self.logger.exception(f"Failed to connect to: {self.peripheral_mac} - {e}")

    async def subscribe(self):
        try:
            services = self.client.services
            for service in services:
                for characteristic in service.characteristics:
                    if characteristic.uuid == self.characteristic_uuid:
                        self.logger.info(f"Subscribing to notifications from: {self.peripheral_mac}")
                        try:
                            await self.client.start_notify(characteristic.uuid, self.notification_handler)
                        except Exception as e:
                            self.logger.exception(f"Could not start notifications from: {self.peripheral_mac} - {e}")
        except Exception as e:
            self.logger.exception(f"Error subscribing to: {self.peripheral_mac} : {e}")


    async def disconnect(self):
        try:
            await self.client.disconnect()
            self.connected = False
            self.logger.info(f"Disconnected from {self.client.address}")
        except Exception as e:
            self.logger.exception(f"Failed to disconnect from: {self.peripheral_mac} - {e}")    