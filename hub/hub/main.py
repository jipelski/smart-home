import asyncio
from hub_manager import HubManager
from config import Config
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    config = Config()
    hub_manager = HubManager(config=config)
    devices = config.DEVICES

    for device_key, device in devices.items():
        await hub_manager.create_and_connect(
                device.get('peripheral_mac'), 
                device.get('service_uuid'), 
                device.get('characteristic_uuid'),
                device.get('structure'),
                device.get('type')
            )
    await hub_manager.start_mqtt()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        for client_key in hub_manager.clients.keys():
            await hub_manager.disconnect_ble_client(client_key)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting gracefully...")