# MQTT to Redis Service

## Description

The `mqtt_to_redis` service acts as a data catcher on the backend. It subscribes to specific MQTT topics and pushes incoming messages to a Redis Stream. This approach allows for decoupled processing of sensor data, and potential horizontal scaling.

## Features

 **MQTT Subscription**: 
 An MQTT client is created, connects to the MQTT Broker, and subscribes to data topics.
 
 **Redis Integration**: 
 Incoming messages are decoded and added to a Redis Stream.

## How it works

- Creates an MQTT client and subscribes to data topics.
- For each incoming message:
  - Decodes the payload
  - Trasforms the data_fields into a JSON string
  - Adds message to Redis Stream

## Setup and Installation

### Requirements

**Software**:
- Access to a Redis server
- Access to an MQTT broker
- Python 3.11 or higher
- `aiomqtt`
- `redis`
-`python-dotenv`

### Run with Docker

- Ensure you have an existing .env file as <a href=".envexample">this</a>.
- Run the following command:
  `docker run -d --env-file .env jipelski/mqtt_to_redis_service_arm64:latest`
- Note: the above command will only work on linx/arm64 platforms

### Run Locally

**Clone the Repository**
```
git clone https://github.com/jipelski/smart-home.git
cd smart-home/back_end/back_end/mqtt_to_redis
```

**Install the Requirements**

`pip install -r requirements.txt`

**Configuration**
- Create an .env file follwing the .envexample file.

**Usage**

Run the hub service using:
`python mqtt_to_redis.py`
