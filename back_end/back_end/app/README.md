# FastAPI Application

## Description

The `app` service is a FastAPI application that provides RESTful APIs and WebSocket endpoints for clients to interact with the smart home system. It allows clients to:

- Retrieve sensor data.
- Receive real-time updates via WebSockets.
- Send commands to hubs (e.g., connect or disconnect devices). # Note: in later versions, some peripherals will be smart switches, which will require other types of commands.

## Features

- **RESTful APIs** for accessing sensor data.
- **WebSocket** endpoints for real-time data updates.
- **MQTT Client** for sending commands to hubs.
- **Database Integration** with PostgreSQL using `asyncpg`.

## Directory Structure
```
+---app
|   database.py
|   dockerfile
|   main.py
|   requirements.txt
|   __init__.py
|
+---models
|     hub.py
|     sensor.py
|
+---routes
|    health.py
|    hub.py
|    sensor.py
|    websocket.py
|
\---services
    db_service.py
    mqtt_service.py
    websocket_manager.py
```

## How it works

### API Endpoints
#### Health Check
- **GET** `/health`
  - **Description**: Check if the API is running.
  - **Response**: `{"status": "OK"}`
  
#### Sensor Data
- **GET** `/sensor-data/{sensor_type}/{sensor_id}`
  - **Description**: Retrieve sensor data for a specific sensor.
  - **Response Model**: `List[SensorDataOut]`

- **GET** `/sensor-data/{sensor_type}`
  - **Description**: Retrieve filtered sensor data.
  - **Query Parameters**:
    - `sensor_id`: Optional
    - `start_time`: Optional `datetime`
    - `end_time`: Optional `datetime`
    - `limit`: Optional `int`
  - **Response Model**: `List[SensorDataOut]`

- **GET** `/sensor-data-latest/{sensor_type}/{sensor_id}`
  - **Description**: Retrieve the latest sensor data.
  - **Response Model**: `SensorDataOut`

- **GET** `/aggregated-sensor-data/{sensor_type}/{sensor_id}`
  - **Description**: Retrieve aggregated data for the specified sensor.
  - **Response Model**: `List[AggrDataOut]`
  

#### Hub Commands
- **POST** `/hubs/{hub_id}/connect_device`
  - **Description**: Send a command to a hub to connect a device.
  - **Request Body**: ConnectDeviceRequest
  - **Response**: `{"status": "Connect command sent", "hub_id": hub_id}`

- **POST** `/hubs/{hub_id}/disconnect_device`
  - **Description**: Send a command to a hub to disconnect a device.
  - **Query Parameter**: `peripheral_mac`
  - **Response**: `{"status": "Disconnect command sent", "hub_id": hub_id}`

#### WebSocket Endpoint
- **WebSocket** `/ws/sensor/{sensor_id}`
  - **Description**: Receive real-time updates for a specific sensor.
  -  **Usage**: Connect via a WebSocket client to receive updates.

### Services
**1. database.py**
  -  Manages the connection to the Postgres database asynchronously using asyncpg.
  -  Initialises the database connection at start-up.

**2. models**
  - `sensor.py`: Defines the Pydantic models for sensor data.
  - `hub.py`: Defines the Pydantic models for hub commands.

**3. routes/**
  - `health.py`: Health check endpoint.
  - `sensor.py`: Sensor data retrieval endpoint.
  - `hub.py`: Hub command posting endpoint.
  - `websocket.py`: WebSocket endpoint.

**4. services/**
  -  `db_service.py`: Holds the functions for data retrieval from the database.
  -  `mqtt_service.py`: Publishes commands to hubs via MQTT.
  -  `websocket_manager.py`: Manages Websocket connections and broadcasts messages.

## Dependencies
  - **FastAPI**
  - **asyncpg**
  - **aiomqtt**
  - **redis.asyncio**
  - **uvicorn**
  - **pydantic**

## Setup and Installation
### Requirements
  - Python 3.11 or higher
  - Access to a Redis server
  - Access to an MQTT Broker
  - Access to Postgres database
  - `python-dotenv`
  - `asyncpg`
  - `fastapi`
  - `aiomqtt`
  - `redis[asyncio]`
  - `uvicorn`
  - `pydantic`

### Run with Docker
  - Ensure you have an existing .env file.
  - Run the following command:
    `docker run -d --env-file .env jipelski/fastapi_service_arm64:latest`
  - Note: the above command will only work on Linux/arm64 platforms

### Run Locally

**Clone the Repository**
```
git clone https://github.com/jipelski/smart-home.git
cd smart-home/back_end/back_end/app
```

**Install the Requirements**

`pip install -r requirements.txt`

**Configuration**

Create a .env file following the .envexample file.

**Usage**

Run the hub service using:
`python main.py`
