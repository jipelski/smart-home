from dotenv import load_dotenv
import os
import logging

class Config():
    def __init__(self):
        load_dotenv()
        self.MQTT_COMMAND_TOPIC = os.getenv('MQTT_COMMAND_TOPIC')
        self.MQTT_DATA_TOPIC = os.getenv('MQTT_DATA_TOPIC')
        self.MQTT_BROKER = os.getenv('MQTT_BROKER')
        self.MQTT_PORT = os.getenv('MQTT_PORT')
        self.MQTT_USERNAME = os.getenv('MQTT_USERNAME')
        self.MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

        self.LOOK_UP_TABLE = os.getenv('LOOK_UP_TABLE')

        logging.basicConfig(
            filename=os.getenv('BLE_LOG_FILE'), 
            format=os.getenv('BLE_LOG_FORMAT'), 
            datefmt=os.getenv('BLE_LOG_DATE_FORMAT') , 
            encoding=os.getenv('BLE_LOG_ENCODING'), 
            level=logging.DEBUG
        )

        self.logger = logging.getLogger("HubManager")