# Hub Service

## Description
The Hub Service Module acts as a central bridge in one location, connecting Bluetooth Low Energy (BLE) sensors to the backend using MQTT. The hub scans for predetermined BLE devices, connects to them, listens to their notifications, and publishes this data to an MQTT topic for further processing.

## Components

**Hardware**
- Raspberry Pi 4 model B with an integrated bluetooth module

**Software**
- `ble_client.py`: Handles BLE client connections and notifications.
- `config.py`: Loads environmental variables and configures logging.
- `hub_manager.py`: Manages BLE clients and MQTT communication.
- `main.py`: Program entry point.

**Module Struture**
```
+---hub
|   |   .envexample        # Example env file
|   |   __init__.py        # __init__ file
|   |   ble_client.py      
|   |   config.py
|   |   dockerfile         # dockerfile needed to build image
|   |   hub_manager.py
|   |   main.py
|   |   requirements.txt   # requirements file
\---test
```

## Features

  **BLE Connectivity**: 
  Connects to multiple BLE peripehral devices and subscribes to their notitications.
  
  **Data Handling**: 
  Unpacks received data using preset data structures and repacks it for transmission.
  
  **MQTT Publishing**: 
  Publishes sensor data to specified MQTT Broker using specified topics.
  
  **Command Handling**: 
  Listens for commands by subscribing to specific command topics to dynamically connect to or disconnect from BLE peripherals.

## Architecture Overview
<img src="assets/Hub_Service_Flowchart.svg" alt="Hub Service Flowchart" />

  **BLE_Sensors**:
  One or more peripheral devices comunicate bidirectionally with a local instance of Hub_Service trough BLE.

  **Hub_Service**:
  Hub_Service acts as a bridge between the connected peripheral devices and MQTT client on the backend. It subscribes to command topics and publishes to sensor update topics.

  **MQTT_Client**:
  MQTT_Client on backend subscribes to sensor update topics, and publishes based on command topics.

## How it works

**Initialisation**
The main script loads environmental variables from and .env file and configures a logger.
It creates a HubManager object and initialises it.
For every device present in a predetermined list of peripherals, it creates a new ble_client and attempts to connect to the peripheral.
Starts an MQTT client and connects to a broker.

**BLE Device Connection**
The ble_client scans for devices using Bleak. 
When it finds a device that matches a specific mac address it attempts to connect to it.
It subscribes to notifications from the specified set of characteristics given.

**Data Retrieval and Handling**
When a ble_client receives notifications, it passes them to the handle_data() in HubManager for handling.
The message is unpacked using a data structure specific to the type of peripheral device it arrived from.
A JSON payload is created with the unpacked sensor data and metadata.

**Data Transmission using MQTT**
The payload is published to the MQTT broker under a specified sensor update topic.

**Command Handling via MQTT**
The hub listens to commands on specified command topics.
Supports commands to connect and disconnect from BLE devices dynamically.

## Setup and Installation

### Requirements
**Hardware**

- A device with a bluetooth module. I am using a **Raspberry Pi 4 Model B**.
- At least 1 peripheral sensor. I am using a **Pico WH** with a mounted **BME688** sensor.

**Software**

Access to an MQTT broker. Either ran locally using **Eclipse Mosquitto** or on the cloud using **HiveMq**.
Python 3.11 or higher
`aiomqtt`
`bleak`
`python-dotenv`
`bluez`
`dbus`
`pip` package manager


**Using Docker**

- Ensure you have an existing .env file as <a href="./hub/.envexample">this</a>.
- Run the following command:
`docker run -d --privileged --net=host --env-file .env --device=/dev/hci0 -v /var/run/dbus:/var/run/dbus jipelski/offsite_hub_service_arm64:latest`
- Note: the above command will only work on linx/arm64 platforms

**Clone the Repository**
```
git clone https://github.com/jipelski/smart-home.git
cd smart-home/hub/hub
```

**Install the Requirements**

`pip install -r requirements.txt`

**Configuration**
- Create an .env file follwing the .envexample file.

**Usage**

Run the hub service using:
`python main.py`


