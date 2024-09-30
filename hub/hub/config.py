from dotenv import load_dotenv
import os

class Config():
    def __init__(self):
        load_dotenv()
        self.MQTT_COMMAND_TOPIC = os.getenv('MQTT_COMMAND_TOPIC')
        self.MQTT_DATA_TOPIC = os.getenv('MQTT_DATA_TOPIC')
        self.MQTT_BROKER = os.getenv('MQTT_BROKER')
        self.MQTT_PORT = os.getenv('MQTT_PORT')
        self.MQTT_USERNAME = os.getenv('MQTT_USERNAME')
        self.MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

        self.BLE_LOG_FILE = os.getenv('BLE_LOG_FILE')
        self.BLE_LOG_FORMAT = os.getenv('BLE_LOG_FORMAT')
        self.BLE_LOG_DATE_FORMAT = os.getenv('BLE_LOG_DATE_FORMAT')
        self.BLE_LOG_ENCODING = os.getenv('BLE_LOG_ENCODING')