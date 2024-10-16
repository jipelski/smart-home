from database import db
from models.sensor import SensorDataOut, BME688Data
from typing import Optional, List
import datetime

async def fetch_sensor_data(sensor_id: str, sensor_type: str):
    async with db.pool.acquire() as connection:
        if sensor_type == 'BME688':
            query = """
                SELECT sensor_id, timestamp, temperature, humidity, pressure, gas_resistance
                FROM BME688
                WHERE sensor_id = $1
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            rows = await connection.fetch(query, sensor_id)
            return [BME688Data(sensor_type='BME688', **dict(row)) for row in rows]
        else:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")
    
async def fetch_latest_sensor_data(sensor_id: str, sensor_type: str) -> Optional[SensorDataOut]:
    async with db.pool.acquire() as connection:
        if sensor_type == 'BME688':
            query = """
                SELECT sensor_id, timestamp, temperature, humidity, pressure, gas_resistance
                FROM BME688
                WHERE sensor_id = $1
                ORDER BY timestamp DESC
                LIMIT 1
            """
            row = await connection.fetchrow(query, sensor_id)
            if row:
                return BME688Data(sensor_type='BME688', **dict(row))
            else:
                return None
        else:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

async def fetch_sensor_data_filtered(
    sensor_id: Optional[str],
    sensor_type: str,
    start_time: Optional[datetime.datetime],
    end_time: Optional[datetime.datetime],
    limit: Optional[int] = 1000
) -> List[SensorDataOut]:
    conditions = []
    values = []

    if sensor_id:
        conditions.append(f"sensor_id = ${len(values) + 1}")
        values.append(sensor_id)
    if start_time:
        conditions.append(f"timestamp >= ${len(values) + 1}")
        values.append(start_time)
    if end_time:
        conditions.append(f"timestamp <= ${len(values) + 1}")
        values.append(end_time)

    async with db.pool.acquire() as connection:
        if sensor_type == 'BME688':
            query = f"""
                SELECT sensor_id, timestamp, temperature, humidity, pressure, gas_resistance
                FROM BME688
                WHERE 1=1
            """
            if conditions:
                query += " AND " + " AND ".join(conditions)
            query += " ORDER BY timestamp DESC"

            if limit is not None:
                query += f" LIMIT ${len(values) + 1}"
                values.append(limit)
            rows = await connection.fetch(query, *values)
            return [BME688Data(sensor_type='BME688', **dict(row)) for row in rows]
        else:
            raise ValueError(f'Unsupported sensor type: {sensor_type}')