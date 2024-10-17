# Redis to Db Service

## Description

The Redis to Db service reads data from a Redis stream, processes it, stores it into a database, and publishes sensor id specific updates to a Redis Pub/Sub mechanism for real-time notifications.

## Features

 **Redis Stream Consumption**: 
 Reads batches of messages from a Redis Stream.
 
 **Data Processing**:
 Validates and transforms data for storage.
 
**Database Insertion**:
Stores sensor data into corresponding tables in PostgreSQL.

**Real-time Updates**: 
Publishes sensor updates to Redis Pub/Sub channels.

## How it works

- Creates and connects Redis client to a Redis server and reads messages from a predefined redis stream.
- For each incoming message:
  - Parses and validates data
  - Inserts data into the appropriate table based on the sensor type
- Publishes sensor id specific data to a Redis Pub/Sub channel for real-time communication.

## Setup and Installation

### Requirements

**Software**:
- Redis server accessible
- MQTT broker accessible
- Python 3.11 or higher
- `asyncpg`
- `redis.asyncio`
- `python-dotenv`

### Run with Docker

- Ensure you have an existing .env file as <a href=".envexample">this</a>.
- Run the following command:
  `docker run -d --env-file .env jipelski/redis_to_db_service_arm64:latest`
- Note: the above command will only work on linx/arm64 platforms

### Run Locally

**Clone the Repository**
```
git clone https://github.com/jipelski/smart-home.git
cd smart-home/back_end/back_end/redis_to_db
```

**Install the Requirements**

`pip install -r requirements.txt`

**Configuration**
- Create an .env file follwing the .envexample file.

**Usage**

Run the hub service using:
`python redis_to_db.py`
