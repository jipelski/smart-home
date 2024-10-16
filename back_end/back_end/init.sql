CREATE TABLE IF NOT EXISTS buildings (
    address VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(255) PRIMARY KEY,
    address VARCHAR(255) REFERENCES buildings(address)
);

CREATE TABLE IF NOT EXISTS abstract_sensors (
    type VARCHAR(50) PRIMARY KEY,
    structure JSONB
);

CREATE TABLE IF NOT EXISTS active_sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    room_id VARCHAR(255) REFERENCES rooms(room_id),
    sensor_type VARCHAR(50) REFERENCES abstract_sensors(type)
);

CREATE TABLE IF NOT EXISTS BME688 (
    sensor_id VARCHAR(50) REFERENCES active_sensors(sensor_id),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    pressure DOUBLE PRECISION NOT NULL,
    gas_resistance DOUBLE PRECISION NOT NULL
);